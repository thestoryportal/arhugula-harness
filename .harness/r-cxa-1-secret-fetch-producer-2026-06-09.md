# R-CXA-1 secret-fetch producer evidence (2026-06-09)

## Disposition

This implementation closes `R-CXA-1` must_pass #1 by adding a workflow-time,
scope-bearing production caller for the AS->IS secret-fetch audit seam:
`RuntimeToolDispatcher` resolves `ToolContract.required_secrets` during an active
workflow `TOOL_STEP` and emits `SecretFetchEvent` through
`RuntimeAsIsWiring.emit_secret_fetch_audit_entry`.

This does not retire `H_T-CXA-1`. The row remains `PARTIAL` pending the separate
must_pass #2 / AS->IS edge-scope audit for the remaining AS source-unit
audit-emission callbacks. The historical bootstrap exclusion remains Reading-D:
`resolve_bootstrap_value(name)` is still name-only provider construction and is
not used as the producer.

## Implementation Evidence

- Production firing site: `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py`
  resolves `contract.required_secrets` after sandbox decision and before tool
  execution, with live workflow id, step id, actor, secret scope, and sandbox
  tier available.
- Production injection: `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py`
  passes `ctx.keyring_resolver` plus
  `RuntimeAsIsWiring(ctx.ledger_writer).emit_secret_fetch_audit_entry` into the
  stage-5 dispatcher.
- Non-hollow metadata: `GcpSecretManagerResolver.resolve_with_audit_metadata`
  returns backend rotation/version metadata from GCP Secret Manager; keyring/env
  fallback fails closed for audit metadata rather than inventing a sentinel
  `secret_last_rotated_at`.
- Observability: every success/failure opens a structure-only `secret.fetch`
  span with secret name, scope, backend, cache overhead, policy reason, and
  failure class when applicable. Secret values are never emitted.

## Verification

- `uv run pytest harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py -k 'secret_fetch or failed_fetch'`
- `uv run pytest harness-runtime/tests/test_config_provider_secrets.py -k 'audit_metadata or gcp_secret_manager_resolve_with_audit_metadata'`
- `uv run pytest harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py`
- `uv run pytest harness-runtime/tests/test_config_provider_secrets.py`
- `uv run pytest harness-runtime/tests/test_bootstrap.py harness-runtime/tests/integration/test_bootstrap_stages.py`
- `/usr/bin/env PYTHONPATH=tools UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py harness-runtime/tests/test_config_provider_secrets.py harness-runtime/tests/test_bootstrap.py harness-runtime/tests/integration/test_bootstrap_stages.py tools/test_dashboard_generate.py tools/test_substitution_ledger.py`
- `uv run pytest harness-runtime/tests/test_u_rt_75_runtime_tool_dispatcher_factory.py harness-runtime/tests/test_lifecycle_providers.py`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `just overlay-check`
- `just --no-dotenv check`
