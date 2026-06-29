# R-CL-Q1 Harness-IS Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-is` package review for later rollup into the final Q1 artifact.

Date: 2026-06-29
Branch: `r-cl-q1-harness-is-review`
Base: `origin/main` at `75cfa112`

## Scope

- `harness-is/src/harness_is/*.py`
- `harness-is/tests/*.py`
- `harness-is/pyproject.toml`

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of all `harness-is` carriers, public exports, package metadata, and cross-axis import consumers. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on path classification, content-addressed prompt versions, JSONL ledger append/read behavior, hash-chain construction, git shell-out edges, worktree isolation, and seam export coverage. | No open findings in `harness-is`. |
| `simplify` | passed | Simplification scan for duplicate carriers, unused abstractions, TODO/FIXME markers, dead branches, silent failures, broad exception handling, and avoidable control flow. | No simplification changes needed in `harness-is`. |

## Harness-IS Observations

- Path and tier registries are closed enum plus frozen metadata carriers:
  `PathClass`, `ArtifactTier`, and `GitTierSubRole` are populated through
  immutable `MappingProxyType` registries; path binding rejects duplicate
  `(path_class, workflow_class, deployment_surface)` triples.
- Path resolution is deliberately configuration-bound. `PathResolver` returns
  exactly the configured path for a requested triple and raises
  `PathBindingMissingError` instead of manufacturing default paths.
- State-ledger data models keep the F-layer entry shape explicit and frozen.
  Optional sidecars (`procedural_tier_snapshot_ref` and `branch_metadata`) are
  additive, omitted from persisted JSONL when absent, and included in canonical
  hash material only when present.
- Hash-chain construction is split into pure functions:
  `canonicalize`, `compute_response_hash`, `construct_prior_event_hash`, and
  `verify_chain` have no filesystem or network side effects.
- JSONL ledger writing is the narrow side-effect edge. `append_ledger_entry`
  checks write-key consistency, serializes the read-prior-then-append critical
  section with a module-level lock, preserves the first payload for repeat
  idempotency keys, computes both hash fields internally, and rejects
  non-monotonic timestamps.
- JSONL ledger reading is bounded by construction. The read API operates over
  an immutable tuple snapshot, requires a `NavigationQuery` plus
  `BoundedWindow`, returns no entries for an unscoped query, and reports
  `next_position` on truncation.
- Prompt manifest carriers are content-addressed. `PromptVersion` derives
  `version_sha` from content, rejects mismatches at construction, and
  `PromptManifest` enforces authored-store uniqueness plus active-version
  membership when a version store is present.
- Git integration stays at explicit edge functions. Atomic deploy verification,
  shadow-Git checkpointing, rollback, and worktree isolation shell out to the
  `git` CLI with typed inputs/results; the pure parts are separately testable.
- Workload opt-ins are default-off and validated: shadow-Git checkpointing
  requires an explicit cadence when enabled, while worktree isolation enforces
  opt-out and concurrency-cap rejection at allocation time.
- `substrate_seam_exports.py` is declarative only and enumerates the six IS
  substrate seam exports with carrier units, consuming axes, and stable
  composition references.
- Package metadata is minimal: `harness-is` depends only on `harness-core`
  inside the uv workspace.

## Simplification Notes

- The only source-level `NotImplementedError` is the abstract
  `NavigationPrimitive.read` interface method.
- The only source-level `Any` / `cast` use is the Pydantic before-validator in
  `PromptVersion`, where raw input may be an arbitrary object before model
  validation.
- `type: ignore` markers are test-only and exercise frozen Pydantic models,
  extra-forbid behavior, or intentionally invalid typed inputs.
- Subprocess usage is confined to git-backed integration primitives and their
  tmp-repository tests; no `shell=True` call sites were found.
- No `TODO` or `FIXME` markers were found in `harness-is`.

## Verification Evidence

- RED artifact witness: `rtk run "test -f .harness/r-cl-q1-harness-is-review.md"`
  failed before this evidence file existed.
- Fresh-worktree direct package test before workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-is/tests -q`
  failed during collection with missing `harness_is` / `harness_core`
  imports. This is the expected editable-sync boundary that `just codex-sync`
  and `just codex-check` cover.
- Workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-sync` passed after fetching
  the package build dependency needed for local workspace wheel builds and
  installing the seven workspace packages.
- Package tests after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-is/tests -q`
  passed with `171 passed`.
- Package typecheck:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pyright harness-is` passed with
  `0 errors, 0 warnings, 0 informations`.
- Package lint:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run ruff check harness-is` passed
  with `All checks passed!`.

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-is` package
evidence. Remaining final Q1 obligations still include `harness-as`,
`harness-cp`, `harness-od`, `harness-cxa`, `harness-runtime`, `tools/`,
`justfile`, `harness.toml.example`, a complete clean-checkout walkthrough, and
a passing fixed-point `just check` record. The provider-free loop gate for this
slice remains `just codex-check`; ambient `just check` is not run by Codex here
because `.env` may load live provider credentials and trigger paid/provider
exercises outside this package evidence slice.
