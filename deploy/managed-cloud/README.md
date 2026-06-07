# R-421 MANAGED_CLOUD Readiness

This directory is the operator-facing setup surface for R-421. It is not a
managed-cloud deployment by itself.

Use `harness.managed-cloud.e2b.example.toml` as the shape of the runtime config
once a managed collector endpoint, cloud provider-secret backend, and hosted
sandbox provider are selected. The current codebase still lacks the
managed-cloud provider-secret backend implementation, so static readiness is
expected to fail on `cloud-secret-backend` until that substrate lands.

After copying the template and replacing placeholders, run:

```bash
just r421-managed-cloud-readiness harness.managed-cloud.toml --hosted-sandbox-provider e2b
```

Optional hosted-sandbox candidate probe:

```bash
uv run --with e2b python tools/r421_e2b_live_probe.py
```

The live E2B probe creates a hosted sandbox and is usage-billed by E2B. It
requires explicit operator approval before Codex runs it.
