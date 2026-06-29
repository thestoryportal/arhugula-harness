# R-CL-Q1 Harness-OD Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-od` package review for later rollup into the final Q1 artifact.

Date: 2026-06-29
Branch: `codex/r-cl-q1-harness-od-review`
Base: local `main` at `c6eee10a` (`ops: roadmap status refresh post-#825 (#826)`)

## Scope

- `harness-od/src/harness_od/*.py`
- `harness-od/tests/*.py`
- `harness-od/pyproject.toml`
- `harness-od/AGENTS.md`

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of the OD package inventory, package metadata, OD-axis instructions, contract overlay carriers, and high-risk audit ledger / cost / redaction / sampling / collector / SQLite span-store surfaces. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on namespace ownership, OTel namespace separation, audit-ledger hashing, cost attribution, redaction fail-closed behavior, sampling policy, local-first collector topology, and SQLite span persistence/readback. | No open findings in `harness-od`. |
| `simplify` | passed | Simplification scan for TODO/FIXME markers, dead stubs, broad catches, silent failures, process/network side effects, env/API-key reads, duplicate carriers, and avoidable control-flow complexity. | No simplification changes needed in `harness-od`. |

## Harness-OD Observations

- `harness-od` contains 57 source `.py` files, `py.typed`, 53 test `.py`
  files, and 23,489 total source/test lines. The package is broad, but the
  reviewed modules are mostly explicit carrier, serializer, namespace,
  sampling, redaction, and local-store witnesses rather than hidden runtime
  side effects.
- Package metadata keeps OD downstream of the axis packages it observes:
  `harness-od` depends on `harness-core`, `harness-as`, `harness-cp`,
  `harness-is`, and OpenTelemetry packages. Direct source review found no
  provider-client construction, API-key reads, live HTTP delivery,
  subprocess, shell, or socket calls in `harness-od`.
- Public package export policy is conservative:
  `harness-od/src/harness_od/__init__.py` is empty, so consumers import
  explicit modules rather than a broad OD re-export surface.
- OD contract grounding is present in the semantic overlay. Queries for
  `C-OD-05`, `C-OD-08`, `C-OD-09`, `C-OD-13`, `C-OD-14`, `C-OD-19`,
  `C-OD-26`, and `C-OD-27` resolve to the expected OD source carriers plus
  CP/CXA/runtime consumers where the contract crosses package boundaries.
- Namespace ownership is explicit. `namespace_map.py` enumerates 15 source-axis
  namespace rows and assertion helpers; the map keeps OD-owned namespace
  authority separate from source-axis and runtime emission sites.
- Audit-ledger carriers in `audit_ledger_types.py` are frozen Pydantic models
  with `extra="forbid"`. Audit payload hashing is a SHA-256 digest over the
  canonical payload JSON, keeping the digest helper deterministic and
  structure-bound.
- Cost-attribution formulas are declarative and fail-loud. `cost_formula.py`
  represents rate entries and explicit price-rate lookups, and missing rate
  tables raise `RateLookupError` instead of silently defaulting to zero or
  ambient provider state.
- Redaction is fail-closed at the multi-tenant boundary. The span processor
  requires a non-empty redacted attribute set for multi-tenant mode, leaves
  solo-developer content capture behind an explicit `ContextVar` toggle, and
  performs best-effort attribute mutation only at the OTel processor boundary.
- The deterministic redaction tokenizer is provider-free. It emits opaque
  token placeholders through an injected token-map sink protocol and does not
  encode raw key/value content, trace IDs, or span IDs in the token string.
- Sampling policy is typed and table-driven. `composite_sampler.py` wraps the
  OD composite sampler in `ParentBased`, honors the always-sampled set before
  ratio sampling, and leaves non-root late-keep behavior to the tail-keep span
  processor rather than adding hidden sampler state.
- SQLite span persistence is parameterized and idempotent. `sqlite_span_store.py`
  uses `CREATE TABLE/INDEX IF NOT EXISTS`, parameterized writes, `INSERT OR
  IGNORE`, and explicit retention deletion. Reader queries parameterize caller
  values and localize tuple-shape typing at the sqlite row coercion boundary.
- `local_first_otlp_collector.py` is a library topology and policy surface. It
  defines collector placement, sink, TUI, and retention carriers, but it does
  not start a live collector, daemon, socket listener, SQLite process, or
  network exporter.

## Simplification Notes

- No source-level `TODO` or `FIXME` markers were found in `harness-od`.
- No source-level provider-client construction, API-key/env-var reads,
  subprocess, shell, HTTP-client, socket, `eval`, or `exec` call sites were
  found in `harness-od`.
- Source `NotImplementedError` hits are comments or downstream CP boundary
  descriptions, not active OD stubs.
- Source `pass` hits are limited to a type-checking block and a documented
  immutable-attribute fallback in the redaction span processor. The latter is
  intentionally scoped to the observability processor boundary so redaction
  bookkeeping cannot fail tracer-provider shutdown.
- `Any`, `cast`, and `type: ignore` occurrences are localized to sqlite row
  coercion, OTel protocol handles, or negative tests. No package-wide loose
  type surface was identified.
- The package intentionally uses many small modules because each one owns a
  separate OD evidence surface. Merging the declarative matrices and carriers
  during Q1 would blur namespace authority without reducing a concrete defect
  or meaningful duplication.

## Verification Evidence

- RED artifact witness:
  `rtk proxy /bin/test -f .harness/r-cl-q1-harness-od-review.md` failed before
  this evidence file existed.
- Source inventory:
  `rtk rg --files harness-od` listed `AGENTS.md`, `CLAUDE.md`,
  `pyproject.toml`, `py.typed`, 57 source `.py` files, and 53 test `.py`
  files.
- Source/test size inventory:
  `rtk wc -l harness-od/src/harness_od/*.py harness-od/tests/*.py` reported
  23,489 total source/test lines.
- Simplification/risk scan:
  `rtk rg -n "TODO|FIXME|NotImplemented|pass$|Any|cast\\(|type: ignore|except Exception|shell=True|subprocess|requests|urllib|httpx|socket|eval\\(|exec\\(|os\\.environ|environ\\[|getenv" harness-od/src/harness_od`
  found expected hits in sqlite tuple typing, comments, type-checking code,
  and the documented redaction fallback; no TODO/FIXME markers or process /
  network / env side effects were found.
- Overlay grounding:
  `rtk just overlay-query --contract C-OD-05`,
  `rtk just overlay-query --contract C-OD-08`,
  `rtk just overlay-query --contract C-OD-09`,
  `rtk just overlay-query --contract C-OD-13`,
  `rtk just overlay-query --contract C-OD-14`,
  `rtk just overlay-query --contract C-OD-19`,
  `rtk just overlay-query --contract C-OD-26`, and
  `rtk just overlay-query --contract C-OD-27` resolved to the expected OD
  carriers and crossing CP/CXA/runtime consumers.
- Fresh-worktree direct package test before workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pytest harness-od/tests -q`
  failed during collection with 52 missing-import errors for `harness_od`,
  `harness_core`, `harness_cp`, and `harness_as`. This is the expected
  editable-sync boundary that `just codex-sync` and `just codex-check` cover.
- Workspace sync:
  escalated `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just codex-sync` passed
  and installed all seven workspace packages.
- Package tests after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pytest harness-od/tests -q`
  passed with `960 passed`.
- Package typecheck:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run pyright harness-od` passed
  with `0 errors, 0 warnings, 0 informations`.
- Package lint:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk uv run ruff check harness-od`
  passed with `All checks passed!`.
- Provider-free PR gate:
  escalated `UV_CACHE_DIR=/tmp/arhugula-uv-cache rtk just codex-check`
  passed with workspace sync, ruff, pyright, and provider-free pytest exit 0.

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-od` package
evidence. Remaining final Q1 obligations still include `harness-cxa`,
`harness-runtime`, `tools/`, `justfile`, `harness.toml.example`, a complete
clean-checkout walkthrough, and a passing fixed-point `just check` record. The
provider-free loop gate for this slice is `just codex-check`; ambient
`just check` is not run by Codex here because `.env` may load live provider
credentials and trigger paid/provider exercises outside this package evidence
slice.
