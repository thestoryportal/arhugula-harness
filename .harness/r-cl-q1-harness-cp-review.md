# R-CL-Q1 Harness-CP Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-cp` package review for later rollup into the final Q1 artifact.

Date: 2026-06-29
Branch: `codex/r-cl-q1-harness-cp-review`
Base: local `main` at `5d47c5e2` (`ops: roadmap status refresh post-#823`)

## Scope

- `harness-cp/src/harness_cp/*.py`
- `harness-cp/tests/*.py`
- `harness-cp/pyproject.toml`
- `harness-cp/AGENTS.md`

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of the CP package inventory, package metadata, CP-axis instructions, contract overlay carriers, and high-risk workflow-driver / pause-resume / HITL / routing surfaces. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on topology dispatch, workflow-driver failure handling, pause/resume snapshots, fan-out and handoff recovery, per-step overrides, gate-level composition, validator hooks, routing, MCP trust evaluation, and CP audit/state-ledger composers. | No open findings in `harness-cp`. |
| `simplify` | passed | Simplification scan for TODO/FIXME markers, dead stubs, broad catches, silent failures, process/network side effects, excessive public exports, duplicate carriers, and avoidable control-flow complexity. | No simplification changes needed in `harness-cp`. |

## Harness-CP Observations

- `harness-cp` is intentionally the largest axis package reviewed so far:
  11,493 lines of `workflow_driver.py`, 1,193 lines of
  `pause_resume_protocol.py`, 946 lines of `pause_resume_protocol_types.py`,
  and 67,423 total package source/test lines. The size comes from explicit
  topology, pause/resume, fan-out, handoff, evaluator-optimizer, and
  workflow-driver witnesses rather than hidden framework behavior.
- CP contract grounding is present in the semantic overlay. Queries for
  `C-CP-19`, `C-CP-25`, `C-CP-26`, and `C-CP-27` resolve to the expected CP
  source carriers plus runtime/OD consumers where the contract crosses package
  boundaries.
- Package metadata is narrow: `harness-cp` depends on `harness-core`,
  `harness-as`, official provider SDK packages, and OpenTelemetry API. Direct
  source review found no provider-client construction, API-key reads, HTTP
  delivery, subprocess, shell, or socket calls in `harness-cp`; provider
  dispatch remains an injected callable boundary and concrete provider calls
  live downstream.
- Public package export policy is conservative: `harness-cp/src/harness_cp/__init__.py`
  is empty, so package consumers import explicit modules rather than a broad
  re-export surface.
- Routing surfaces are typed and boundary-oriented. `InferenceRequest`,
  `InferenceResponse`, `ProviderDispatchResult`, and `ProviderDispatchFn`
  keep the CP routing core pure while allowing runtime provider adapters to
  supply the side-effectful dispatch callable. The Layer-3 router path is
  budget-bound and malformed or missing candidates fail through a typed
  `RoutingCandidateUnresolvedError`.
- Gate-level composition is centralized in `gate_level_rule.py`. The four
  gate axes compose through rank-based `max()`, `mcp_trust` is floor-only and
  not override-able, and persona/blast overrides are explicit fields rather
  than ambient policy checks.
- Per-step override resolution keeps each override dimension separate.
  `StepEffectiveBinding` carries concrete model/engine decisions plus
  `None`-or-override signals for model, prompt, role, and removal directives.
  The loosened HITL-placement set is a closed enum carrier, making disallowed
  placements unrepresentable at the CP type boundary.
- MCP trust evaluation is table-driven and fail-closed at the decision layer:
  deny-list wins, known-server tier floors are explicit, unknown-server
  decisions always require audit, and non-conservative unknown-server tier
  derivation requires an injected resolver instead of silently defaulting.
- Pause/resume carriers are frozen Pydantic models with `extra="forbid"`.
  The protocol splits immutable snapshot/result/context records from the
  concrete protocol behavior, and workflow-driver resume guards check
  topology-carrier compatibility before replaying captured state.
- `workflow_driver.py` uses explicit typed exceptions and status mappings for
  setup failures, step-dispatch failures, pause capture, effect-fence pauses,
  validator escalation, fan-out ambiguity, and handoff failure. Broad
  `except Exception` paths reviewed in source are localized failure-disposition
  boundaries or documented best-effort observability hooks.
- Validator framework hook failures are intentionally swallowed only at the
  post-evaluate observability hook, with the inline invariant that
  observability must not fail dispatch. Core validator outcome conversion
  remains typed through `ValidatorOutcome`, `ValidatorNextAction`,
  `ValidatorFailClass`, and `ValidatorEvaluation`.
- The source `NotImplementedError` hits are deliberate boundary stubs or
  substrate-not-bound sentinels: operator-burden aggregation, webhook delivery,
  provider cache completion, signature verification delegation, CP-side
  HITL-gate signature-only surface, and engine pause/resume substrate absence.
  Each names the downstream integration owner instead of silently inventing
  missing behavior inside CP.

## Simplification Notes

- No source-level `TODO` or `FIXME` markers were found in `harness-cp`.
- No source-level subprocess, shell, HTTP-client, socket, env-var, or provider
  client construction call sites were found in `harness-cp`.
- `Any`, `cast`, and `type: ignore` occurrences are concentrated in protocol
  boundaries, opaque manifest payloads, OTel span handles, test fakes, or
  Pydantic negative tests. The source comments generally explain the package
  dependency boundary being preserved.
- The empty package `__init__.py` avoids a large unstable public API surface.
  The explicit module-level API style is appropriate for this package.
- `workflow_driver.py` is large, but the current decomposition keeps the
  topology strategies and their shared helper state in one driver authority.
  Splitting it during Q1 would risk moving behavior without reducing a
  concrete duplication or defect; no surgical simplification was identified.

## Verification Evidence

- RED artifact witness:
  `rtk proxy /bin/test -f .harness/r-cl-q1-harness-cp-review.md` failed before
  this evidence file existed.
- Source inventory:
  `rtk rg --files harness-cp` listed `AGENTS.md`, `CLAUDE.md`, `pyproject.toml`,
  `py.typed`, 72 source `.py` files, and 105 test `.py` files.
- Source/test size inventory:
  `rtk wc -l harness-cp/src/harness_cp/*.py harness-cp/tests/*.py` reported
  67,423 total source/test lines.
- Simplification/risk scan:
  `rtk rg -n "TODO|FIXME|NotImplemented|pass$|Any|cast\\(|type: ignore|except Exception|shell=True|subprocess|requests|urllib|httpx|eval\\(|exec\\(" harness-cp/src/harness_cp harness-cp/tests`
  found expected hits in tests and documented CP boundary surfaces; source-only
  follow-up found no TODO/FIXME markers and no process/network side effects.
- Overlay grounding:
  `rtk just overlay-query --contract C-CP-19`,
  `rtk just overlay-query --contract C-CP-25`,
  `rtk just overlay-query --contract C-CP-26`, and
  `rtk just overlay-query --contract C-CP-27` resolved to the expected CP
  carriers and crossing runtime/OD consumers.
- Fresh-worktree direct package test before workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-cp/tests -q`
  failed during collection with missing `harness_cp`, `harness_core`, and
  `harness_as` imports. This is the expected editable-sync boundary that
  `just codex-sync` and `just codex-check` cover.
- Workspace sync:
  sandboxed `UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-sync` failed because
  the fresh worktree needed to fetch the `hatchling` build backend and DNS was
  blocked; escalated rerun of the same command passed and installed all seven
  workspace packages.
- Package tests after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-cp/tests -q`
  passed with `1461 passed, 1 xfailed`.
- Package typecheck:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pyright harness-cp` passed with
  `0 errors, 0 warnings, 0 informations`.
- Package lint:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run ruff check harness-cp` passed with
  `All checks passed!`.
- Provider-free PR gate:
  sandboxed `UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-check` passed sync,
  ruff, and pyright, then failed at
  `harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py` because
  the sandbox denied binding a local `127.0.0.1` test port. Escalated rerun of
  the provider-free command passed after the corrected artifact diff with sync,
  ruff, pyright, and provider-free pytest exit 0.

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-cp` package
evidence. Remaining final Q1 obligations still include `harness-od`,
`harness-cxa`, `harness-runtime`, `tools/`, `justfile`,
`harness.toml.example`, a complete clean-checkout walkthrough, and a passing
fixed-point `just check` record. The provider-free loop gate for this slice is
`just codex-check`; ambient `just check` is not run by Codex here because
`.env` may load live provider credentials and trigger paid/provider exercises
outside this package evidence slice.
