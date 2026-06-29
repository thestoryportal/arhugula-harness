# R-CL-Q1 Harness-CXA Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-cxa` package review for later rollup into the final Q1 artifact.

Date: 2026-06-29
Branch: `codex/r-cl-q1-harness-cxa-review`
Base: local `main` at `40ebd220` (`ops: roadmap status refresh post-#827 (#828)`)

## Scope

- `harness-cxa/src/harness_cxa/*.py`
- `harness-cxa/tests/*.py`
- `harness-cxa/pyproject.toml`

There is no package-local `harness-cxa/AGENTS.md`; the root Codex
compatibility instructions apply to this package review.

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of the CXA package inventory, package metadata, cross-axis import surface, CP-to-OD audit converter, and semantic overlay carriers for the cited contracts and units. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on carrier-union coverage, audit namespace projection, conditional field elision, prior-hash propagation, `entry_core` fallback behavior, signing/hash delegation, and unsupported-carrier failure behavior. | No open findings in `harness-cxa`. |
| `simplify` | passed | Simplification scan for TODO/FIXME markers, dead stubs, broad catches, silent failures, process/network side effects, env/API-key reads, duplicate signature/hash logic, and avoidable abstractions. | No simplification changes needed in `harness-cxa`. |

## Harness-CXA Observations

- `harness-cxa` contains 2 source `.py` files, `py.typed`, 3 test `.py`
  files, and 925 total source/test lines. The package is intentionally narrow:
  `__init__.py` is empty and the only source module is the CP-to-OD audit-write
  converter.
- Package metadata keeps CXA at the cross-axis boundary. `harness-cxa` depends
  on `harness-core`, `harness-is`, `harness-as`, `harness-cp`, and
  `harness-od`; the package defines no scripts and source review found no
  provider-client construction, API-key/env reads, subprocess, shell, HTTP, or
  socket call sites.
- The main module centralizes the CP-to-OD audit seam in
  `cp_audit_conversion.py`. It imports the CP `CPAuditLedgerEntry`, OD
  producer-specific audit payload types, and OD signature/hash helpers instead
  of duplicating downstream carrier or cryptographic behavior locally.
- `CpAuditCarrier` is a closed union over `CPAuditLedgerEntry` plus the six
  producer-specific OD audit payload subclasses: webhook delivery, operator
  burden, validator escalation, MCP trust, pause/resume, and cost record.
- Namespace projection is explicit. CP-origin fields land under `audit.cp.*`;
  producer-specific fields land under the relevant `audit.hitl_webhook.*`,
  `audit.operator_burden.*`, `audit.validator.*`, `audit.mcp_trust.*`,
  `audit.pause_resume.*`, or `audit.cost.*` prefix.
- Conditional fields are elided rather than emitted with sentinel values:
  CP response hashes appear only when populated, and producer payload fields
  with `None` values are skipped by `_project_producer_namespace_attrs`.
- `entry_core` is caller-supplied when production has a real IS reference. The
  fallback `cp-audit:<action_id>` marker is confined to legacy/test callers and
  keeps omitted entry cores visible instead of silently inventing a ledger ref.
- OD owns signing and payload hashing. The converter delegates to
  `sign_audit_entry` and `compute_entry_hash`, then returns a signed
  `AuditLedgerEntry`.
- Failure behavior is loud: unsupported carrier types raise `TypeError`, and
  an empty `key_id` propagates the OD signer `ValueError`.
- Tests cover baseline CP conversion, `audit.cp.*` projection, response-hash
  conditional elision, entry-core override and fallback behavior, hash-chain
  verification, deterministic entry hashes, empty-key failure, producer-specific
  namespace branches, branch distinctness, cost/pause/resume coverage, and the
  unsupported-carrier negative path.

## Simplification Notes

- No source-level or test-level `TODO`, `FIXME`, `NotImplemented`, active
  `pass`, broad `except Exception`, subprocess, shell, HTTP-client, socket,
  env-var, `eval`, or `exec` call sites were found in `harness-cxa`.
- The only source `type: ignore` is the final `CostRecordAuditPayload`
  `isinstance` branch, suppressing a Pyright false positive caused by the
  preceding exhaustive union narrowing. The only test `type: ignore` passes a
  deliberately invalid carrier to exercise the `TypeError` path.
- The package is already at the smallest useful abstraction: one seam module,
  an empty package export file, and direct tests. Splitting the converter or
  adding another wrapper would add indirection without reducing duplication or
  risk.

## Verification Evidence

- RED artifact witness:
  `rtk proxy /bin/test -f .harness/r-cl-q1-harness-cxa-review.md` failed before
  this evidence file existed.
- Source inventory:
  `rtk rg --files harness-cxa` listed `pyproject.toml`, `py.typed`, 2 source
  `.py` files, and 3 test `.py` files.
- Source/test size inventory:
  `rtk wc -l harness-cxa/src/harness_cxa/*.py harness-cxa/tests/*.py` reported
  925 total source/test lines.
- Simplification/risk scan:
  `rtk rg -n "TODO|FIXME|NotImplemented|pass$|Any|cast\\(|type: ignore|except Exception|shell=True|subprocess|requests|urllib|httpx|socket|eval\\(|exec\\(|os\\.environ|environ\\[|getenv" harness-cxa/src/harness_cxa harness-cxa/tests`
  found only the expected source false-positive suppression and the negative
  unsupported-carrier test suppression.
- Overlay grounding:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just overlay-query --contract C-OD-05`,
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just overlay-query --contract C-OD-24`,
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just overlay-query --contract C-OD-26`,
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just overlay-query --contract C-CP-16`,
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just overlay-query --unit U-CP-72`, and
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just overlay-query --unit U-RT-59`
  resolved to `harness-cxa/src/harness_cxa/cp_audit_conversion.py` plus the
  expected CP, OD, and runtime crossing carriers.
- Fresh-worktree direct package test before workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pytest harness-cxa/tests -q`
  failed during collection with missing imports for `harness_as` and
  `harness_cxa`. This is the expected editable-sync boundary that
  `just codex-sync` and `just codex-check` cover.
- Fresh-worktree direct package typecheck before workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pyright harness-cxa` failed
  with missing workspace imports and unknown types at the same editable-sync
  boundary.
- Pre-sync package lint:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run ruff check harness-cxa`
  passed with `All checks passed!`.
- Workspace sync:
  escalated `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just codex-sync` passed
  and installed all seven workspace packages.
- Package tests after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pytest harness-cxa/tests -q`
  passed with `28 passed`.
- Package typecheck:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pyright harness-cxa` passed
  with `0 errors, 0 warnings, 0 informations`.
- Package lint:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run ruff check harness-cxa`
  passed with `All checks passed!`.
- Provider-free PR gate:
  escalated `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just codex-check`
  passed with workspace sync, ruff, pyright, and provider-free pytest exit 0.

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-cxa` package
evidence. Remaining final Q1 obligations still include `harness-runtime`,
`tools/`, `justfile`,
`harness.toml.example`, a complete clean-checkout walkthrough, and a passing
fixed-point `just check` record. The provider-free loop gate for this slice is
`just codex-check`; ambient `just check` is not run by Codex here because
`.env` may load live provider credentials and trigger paid/provider exercises
outside this package evidence slice.
