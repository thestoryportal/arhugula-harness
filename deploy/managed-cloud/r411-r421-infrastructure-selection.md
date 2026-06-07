# R-411/R-421 Infrastructure Selection

Date: 2026-06-07

Purpose: record the operator-present research pass for compatible R-411 sandbox
host/runtime and R-421 managed-cloud infrastructure choices. This note is a
selection and resume surface; it does not close either roadmap item by itself.

## NotebookLM Access Audit

Notebook used: [Agent Harness Engineering](https://notebooklm.google.com/notebook/57b8d946-830c-42dd-b201-ac117a8af951)

Access paths attempted:

- Codex app tool discovery: no callable NotebookLM MCP tool was exposed; only
  GitHub, Google Drive, node REPL, and Dropbox tools were visible.
- Project MCP config: `.mcp.json` declares `notebooklm` via
  `notebooklm-mcp --transport stdio`, but `codex mcp list` did not expose that
  server in this Codex app session.
- Installed CLIs: `notebooklm`, `nlm`, and `notebooklm-mcp` were present.
- `notebooklm auth check --test --json` passed with live token fetch.
- `notebooklm source list -n 57b8d946-830c-42dd-b201-ac117a8af951 --json`
  returned 40 ready sources.
- `notebooklm ask -n 57b8d946-830c-42dd-b201-ac117a8af951 --json ...`
  returned the R-411/R-421 setup recommendation.
- `nlm login --check` passed and `nlm notebook get
  57b8d946-830c-42dd-b201-ac117a8af951` returned the same 40-source notebook.

NotebookLM's useful result: E2B plus a cloud secret manager and managed
observability backend is the fastest multi-LLM managed-cloud path. NotebookLM
also flagged the same taxonomy mismatch the repo already tracks: E2B can feel
local through its SDK, but execution happens remotely, so it should not be
counted as a local R-411 runtime unless the roadmap taxonomy is deliberately
changed.

## Repo-Grounded Boundary

R-411 remains a local/provider runtime gate. Current operator host checks on
Darwin x86_64 fail all reviewed local R-411 providers:

- `r411-gvisor`: needs Linux plus `runsc` and Docker.
- `r411-kata`: needs Linux plus KVM and `kata-runtime`.
- `r411-shuru`: needs Apple Silicon macOS or Linux ARM64/KVM.
- `r411-microsandbox`: needs Apple Silicon macOS or Linux/KVM.
- `r411-libkrun`: needs Apple Silicon/HVF or Linux/KVM plus libkrun.

R-421 remains a managed-cloud gate. PR #334 landed the static readiness and E2B
probe surfaces, and the approved E2B live probe passed this session with a
deterministic hosted sandbox command. The remaining hard gaps are a landed
managed-cloud `ProviderSecretBackend` selector/resolver and a provisioned
managed collector/OTLP endpoint.

## Recommended Path

### R-411: Linux + gVisor first

Select a Linux x86_64 or ARM64 host with Docker and gVisor `runsc` for the first
R-411 provider implementation. This is the smallest no-taxonomy-change route:
it extends the R-410 Docker execution-driver shape while increasing isolation
with gVisor. The official gVisor install docs support Linux x86_64/ARM64 and
show Docker runtime setup with `runsc install`:
[gvisor.dev/docs/user_guide/install](https://gvisor.dev/docs/user_guide/install/).

Kata is the stronger second R-411 candidate when a Linux KVM host is available.
It is a VM-backed container runtime and aligns with the tier-3 microVM intent,
but it has higher host and orchestration overhead. The project source describes
Kata as lightweight VMs that feel and perform like containers:
[github.com/kata-containers/kata-containers](https://github.com/kata-containers/kata-containers).

Do not spend more time trying to install Firecracker on this Mac for R-411.
Firecracker and QEMU `microvm` belong to R-412/FULL_VM in this repo's current
taxonomy. They need Linux/KVM, and R-412 also gates on a real managed-cloud
surface.

### R-421: E2B + GCP Secret Manager + Google Cloud OTel Collector

Select E2B as the hosted sandbox candidate, GCP Secret Manager as the first
managed-cloud provider-secret backend, and the Google-built OpenTelemetry
Collector on Cloud Run exporting into Google Cloud Observability as the first
managed collector path.

Why this is the fastest honest closure:

- E2B has already passed the approved live probe in this repo session, so the
  hosted sandbox risk is lower than the cloud-secret and collector gaps.
- GCP Secret Manager is cheap at probe scale and has a small selector surface:
  secret version access plus IAM service-account auth. Current pricing lists
  6 active versions and 10,000 access operations/month free, then $0.03 per
  10,000 access operations and about $0.06 per active secret version/month:
  [cloud.google.com/secret-manager/pricing](https://cloud.google.com/secret-manager/pricing).
- Google's Cloud Run OTel Collector guide gives a concrete managed collector
  deployment shape for OTLP logs, metrics, and traces:
  [docs.cloud.google.com/.../opentelemetry-collector-cloud-run](https://docs.cloud.google.com/stackdriver/docs/instrumentation/opentelemetry-collector-cloud-run).
- This keeps the first R-421 implementation to one sandbox vendor and one cloud
  account, instead of combining E2B, a separate secret vendor, and a separate
  observability SaaS on the first pass.

Credentials/operators needed:

- `E2B_API_KEY` for the hosted sandbox probe/e2e.
- GCP project with billing enabled. Runtime config must use the canonical
  project ID or numeric project number, not the display name. The
  operator-provisioned project for this session is
  `project-ba535aa4-f08d-46b2-ba6`; `My First Project` is only the display
  name.
- GCP service account or application-default credentials with Secret Manager
  access and Cloud Run/Observability permissions.
- A non-loopback OTLP endpoint for the managed collector.
- Any LLM provider keys used by the e2e, stored in the selected cloud secret
  backend rather than ambient env fallback.

Estimated cost posture:

- E2B: usage-based; current docs show Hobby at $0/month with one-time credits,
  Pro at $150/month for higher limits, and per-second compute billing:
  [e2b.dev/docs/billing](https://e2b.dev/docs/billing).
- GCP Secret Manager: likely free or cents/month for a small probe if kept
  under free-tier secret/access limits.
- Cloud Run collector and Google Cloud Observability: usage-based; expected low
  for intermittent probes, but use the Google Cloud calculator before leaving a
  continuous collector online.
- LLM provider calls: separate token costs if the R-421 e2e exercises live LLM
  inference. The E2B probe added by PR #334 does not perform LLM inference.

## Alternatives

### E2B + AWS Secrets Manager + Langfuse Cloud

This is strong if the operator prefers AWS or wants an LLM-native UI sooner.
AWS Secrets Manager pricing is currently $0.40/secret/month plus $0.05 per
10,000 API calls in AWS's examples:
[aws.amazon.com/secrets-manager/pricing](https://aws.amazon.com/secrets-manager/pricing/).
Langfuse Cloud currently has a free Hobby plan with 50k units/month, Core at
$29/month, and Pro at $199/month:
[langfuse.com/pricing](https://langfuse.com/pricing).

Pros: mature secret lifecycle, LLM-specific trace UI, multi-LLM friendly.
Cons: more vendors on the first closure path and a higher chance that cost,
auth, and OTLP semantics get debugged at the same time.

### E2B + Arize AX

Arize AX is viable when managed AI observability matters more than staying
inside a single cloud account. Current pricing lists AX Free with 25k spans/month
and AX Pro at $50/month:
[arize.com/pricing](https://arize.com/pricing).

Pros: purpose-built AI/agent observability, managed SaaS path.
Cons: another vendor surface before the base R-421 cloud-secret selector lands.

### Anthropic managed agents / native platforms

NotebookLM surfaced Anthropic managed agents and integrated platforms as fast
paths for agent runtime, sandboxing, and lifecycle management. Do not select
this for current R-421 closure unless the roadmap is intentionally narrowed to a
Claude-centered managed-agents surface. The current harness roadmap keeps
multi-provider runtime/provider-secret behavior load-bearing, and `R-820` is
the deferred managed-agents integration row.

## Implementation Status

The first no-live-call R-421 code slice adds the `gcp-secret-manager`
`ProviderSecretBackend`, a mockable GCP Secret Manager resolver behind
`ProviderSecretsConfig`, provider-free resolver/readiness coverage, and an
E2B + GCP managed-cloud config template. The follow-on connection slice adds
the committed `google-cloud-secret-manager` dependency and extends the E2B
probe so it can resolve `E2B_API_KEY` from the configured backend before
creating a hosted sandbox. Static readiness now passes for the selected shape
without starting the daemon, probing OTLP, fetching secrets, or making
managed-cloud provider calls.

## Remaining Live Closure Slice

1. Provision GCP credentials with Secret Manager access.
2. Run the live R-421 path in the project environment, which now provides
   `google-cloud-secret-manager`.
3. Create the named Secret Manager entries, starting with `e2b-secret` under
   the configured GCP project.
4. Provision a non-loopback managed OTLP endpoint, using the Google-built
   OpenTelemetry Collector on Cloud Run path unless the operator chooses an
   alternate managed collector.
5. Run the resolve-only probe to fetch `E2B_API_KEY` from GCP Secret Manager
   without creating an E2B sandbox.
6. Confirm the cost gate, then run the R-421 live e2e that creates an E2B
   sandbox, emits OTLP to the managed collector, and reports hosted-provider
   calls and cost posture.

R-411 can proceed in parallel only after a compatible Linux host/runtime or
Apple Silicon host is available. Without that host, the honest next local work
is the R-421 live managed-cloud e2e once the operator-provisioned GCP/OTLP
inputs exist.
