# R-421 MANAGED_CLOUD Readiness

This directory is the operator-facing setup surface for R-421. It is not a
managed-cloud deployment by itself.

Use `harness.managed-cloud.e2b.example.toml` as the shape of the runtime config
once a managed collector endpoint, GCP Secret Manager project, and hosted
sandbox provider are selected. Static readiness validates the non-mutating
shape only; it does not fetch GCP secrets, create an E2B sandbox, or probe OTLP.
Set `runtime.provider_secrets.gcp_project_id` to the canonical Google Cloud
project ID or numeric project number, not the console display name. For the
operator-provisioned project from this session, that ID is
`project-ba535aa4-f08d-46b2-ba6`; the display name `My First Project` is not a
valid Secret Manager resource identifier.

The current infrastructure selection is recorded in
[`r411-r421-infrastructure-selection.md`](r411-r421-infrastructure-selection.md).
Recommended first R-421 closure path: E2B hosted sandbox, GCP Secret Manager as
the first managed-cloud provider-secret backend, and the Google-built
OpenTelemetry Collector on Cloud Run exporting to Google Cloud Observability.
R-411 remains a separate host/runtime gate; E2B is not counted as a local R-411
runtime under the current roadmap taxonomy.

After copying the template and replacing placeholders, run:

```bash
just r421-managed-cloud-readiness harness.managed-cloud.toml --hosted-sandbox-provider e2b
```

Credential placement for live GCP probes:

- Preferred operator ADC path: run `gcloud auth application-default login` and
  set the active project to `project-ba535aa4-f08d-46b2-ba6`. The Google SDK
  discovers `~/.config/gcloud/application_default_credentials.json`
  automatically; do not commit that file.
- Service-account path: place the JSON outside the repository, for example
  `/Users/robertrhu/.config/arhugula/gcp-secret-manager-accessor.json`, then
  expose only `GOOGLE_APPLICATION_CREDENTIALS=/Users/robertrhu/.config/arhugula/gcp-secret-manager-accessor.json`
  in the shell or local ignored env file used for the live probe. The service
  account needs Secret Manager Secret Accessor for `e2b-secret`.

To verify that the configured provider-secret backend can fetch the E2B key
without creating a hosted sandbox, run:

```bash
uv run python tools/r421_e2b_live_probe.py --config harness.managed-cloud.toml --resolve-only
```

Optional hosted-sandbox candidate probe after the resolve-only check:

```bash
uv run --with e2b python tools/r421_e2b_live_probe.py --config harness.managed-cloud.toml
```

The live E2B probe creates a hosted sandbox and is usage-billed by E2B. It
requires explicit operator approval before Codex runs it. The resolve-only
command performs a GCP Secret Manager access but does not create an E2B sandbox.

Full R-421 closure still requires operator-provisioned GCP credentials with
Secret Manager access, the named secret entries, a non-loopback managed OTLP
endpoint, a Python environment that provides `google-cloud-secret-manager`,
and explicit approval for live GCP/E2B calls.
