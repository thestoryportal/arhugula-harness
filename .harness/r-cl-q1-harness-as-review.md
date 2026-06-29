# R-CL-Q1 Harness-AS Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-as` package review for later rollup into the final Q1 artifact.

Date: 2026-06-29
Branch: `r-cl-q1-harness-as-review`
Base: local `main` at `6d414a03` (`ops: roadmap status refresh post-#821 (#822)`)

## Scope

- `harness-as/src/harness_as/*.py`
- `harness-as/tests/*.py`
- `harness-as/pyproject.toml`
- `harness-as/AGENTS.md`

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of all `harness-as` carriers, public exports, package metadata, and AS-axis guidance. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on sandbox-tier composition, MCP transport/trust floors, tool-contract validation, secret-fetch and audit structures, sensitive-data exclusion, Anthropic primitive matrices, and seam-export coverage. | No open findings in `harness-as`. |
| `simplify` | passed | Simplification scan for duplicate carriers, unused abstractions, TODO/FIXME markers, dead branches, silent failures, broad exception handling, network/process side effects, and avoidable control flow. | No simplification changes needed in `harness-as`. |

## Harness-AS Observations

- Foundational AS discriminators are closed enum carriers. `MCPTransport` stays
  AS-owned, while `DeploymentSurface` and `PersonaTier` are re-exported from
  `harness-core` instead of locally redeclared.
- Sandbox-tier policy is factored into small pure carriers and table lookups:
  `SandboxTier`, `MechanismClass`, `BlastRadiusTier`, `ToolMetadata`,
  `MCPServerTrustLevel`, `MCPServer`, and `SandboxTierFloorResult` are frozen
  or enum-backed. Remote MCP trust level 0 is represented by a typed `REFUSE`
  result, not by overloading a tier value.
- `sandbox_tier` composes forced-tier rules, contract minimums, blast-radius
  floors, MCP trust floors, the `sandbox_tier_floor` lookup, and injected
  operator-policy floors through monotonic max-ranking. Forced computer-use or
  code-execution conditions short-circuit to full VM; `REFUSE` propagates as a
  distinct composition outcome.
- Deployment and sub-agent tier logic preserve monotonicity. The deployment
  matrix is a 12-cell `(DeploymentSurface, BlastRadiusTier)` map, forcing
  conditions route to the external-irreversible column, and sub-agent dispatch
  returns `max(parent, child_floor)` while flagging downgrade attempts.
- Tool-contract registration keeps pre-validation and validated shapes
  separate. `RawContractInput` admits missing required tier fields so the
  validator can return typed failure outcomes; a `ToolContract` only exists
  after both `minimum_tier` and `blast_radius_tier` are present.
- Secret handling uses opaque, structure-only carriers. `SecretRef` contains
  name, scope, and tier metadata but no value accessor; `fetch_secret` holds no
  in-process cache; allowlist checks are an intersection between tool-required
  secrets and operator policy.
- Secret audit and telemetry avoid value material. `compute_outputs_hash`
  hashes only secret name, scope, and rotation timestamp; audit entries reuse
  the IS `StateLedgerEntry` shape; span attributes carry no secret value field
  and reject malformed success/failure outcomes.
- Sensitive-data discipline is explicit at both sandbox and secret surfaces.
  `SENSITIVE_DATA_EXCLUSIONS` rejects raw tool I/O, resident filesystem state,
  screenshot context, and secret values; redaction helpers are marker-based
  placeholders for the deferred production detector.
- MCP protocol fail classes remain separate from sandbox process fail classes.
  The projection function is total over the four MCP fail classes and preserves
  the dual-attribute emission discipline for `sandbox.violation`.
- Anthropic primitive adoption is data-driven. The 11 primitive enum, 44-cell
  adoption-depth matrix, 20-cell model-binding matrix, graceful-degradation
  policy, cross-family fallback chain, and six attribute namespaces are closed
  maps over the package's enum domains. Surface-conditioned cells preserve the
  full prose in notes rather than adding hidden control-flow branches.
- `as_substrate_seam_exports.py` is declarative only and enumerates the seven
  AS substrate seam exports with carrier units, downstream consuming axes, and
  stable composition references.
- Package metadata is minimal for this axis: `harness-as` depends on
  `harness-core`, `harness-is`, MCP, and OpenTelemetry packages; no package
  scripts or hidden side-effect entry points are declared.

## Simplification Notes

- No source-level `TODO` or `FIXME` markers were found in `harness-as`.
- No source-level `NotImplementedError`, broad `except Exception`, `Any`,
  `cast`, `type: ignore`, subprocess, shell, or network-client call sites were
  found in `harness-as`.
- The package uses repeated small table modules intentionally: each table owns
  a different contract surface, and merging them would blur AS layer
  boundaries without reducing runtime complexity.
- `__init__.py` is long because it is an explicit public re-export surface for
  the axis; tests assert public reexports for selected carrier extensions.
- The code mostly computes or declares data. Side-effectful work such as
  secret value resolution, OTel span delivery, state-ledger append, MCP
  runtime dispatch, and production secret detection stays downstream of this
  package boundary.

## Verification Evidence

- RED artifact witness:
  `rtk proxy /bin/test -f .harness/r-cl-q1-harness-as-review.md` failed before
  this evidence file existed.
- Source inventory:
  `rtk rg --files harness-as` listed 34 source files, `py.typed`, 35 test
  files, `pyproject.toml`, `AGENTS.md`, and `CLAUDE.md`.
- Source/test size inventory:
  `rtk wc -l harness-as/src/harness_as/*.py harness-as/tests/*.py` reported
  8,900 total source/test lines.
- Simplification/risk scan:
  `rtk rg -n "TODO|FIXME|NotImplemented|pass$|Any|cast\\(|type: ignore|except Exception|shell=True|subprocess|requests|urllib|httpx|eval\\(|exec\\(" harness-as/src/harness_as harness-as/tests`
  found no matches.
- Fresh-worktree direct package test before workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-as/tests -q`
  failed during collection with missing `harness_as` imports. This is the
  expected editable-sync boundary that `just codex-sync` and `just codex-check`
  cover.
- Workspace sync:
  sandboxed `UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-sync` failed because
  the fresh worktree needed to fetch the `hatchling` build backend and DNS was
  blocked; escalated rerun of the same command passed and installed all seven
  workspace packages.
- Package tests after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-as/tests -q`
  passed with `318 passed`.
- Package typecheck:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pyright harness-as` passed with
  `0 errors, 0 warnings, 0 informations`.
- Package lint:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run ruff check harness-as` passed with
  `All checks passed!`.
- Provider-free PR gate:
  sandboxed `UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-check` passed sync,
  ruff, and pyright, then failed at
  `harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py` because
  the sandbox denied binding a local `127.0.0.1` test port. Escalated rerun of
  the same provider-free command passed with `5132 passed, 10 skipped,
  24 deselected, 1 xfailed`.

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-as` package
evidence. Remaining final Q1 obligations still include `harness-cp`,
`harness-od`, `harness-cxa`, `harness-runtime`, `tools/`, `justfile`,
`harness.toml.example`, a complete clean-checkout walkthrough, and a passing
fixed-point `just check` record. The provider-free loop gate for this slice is
`just codex-check`; ambient `just check` is not run by Codex here because
`.env` may load live provider credentials and trigger paid/provider exercises
outside this package evidence slice.
