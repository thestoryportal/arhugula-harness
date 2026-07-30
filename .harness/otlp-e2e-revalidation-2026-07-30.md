# OTLP live-e2e re-validation — 2026-07-30

The three OTLP live e2es carried as a standing operator gate since the 2026-06-10 RC close
(runbook `.harness/release-candidate-deployment-readiness-runbook.md` §5 "Current state" bullet 1)
were re-validated end-to-end. All three PASSED on first post-billing attempt.

## Gate resolution chain

1. Operator approved "Grant now, run e2es" (AskUserQuestion, 2026-07-30) and later granted
   standing merge + IAM-grant permissions in-session.
2. `roles/iam.serviceAccountTokenCreator` (`user:storyportalrobert@gmail.com` on SA
   `gcp-secret-manager-accessor@project-ba535aa4-f08d-46b2-ba6.iam.gserviceaccount.com`)
   applied by the agent under that standing authorization; verified in the SA policy.
3. First r421 attempt failed FAST and free at provider-secret resolution
   (`secret_unavailable: e2b-secret`): **GCP project billing was disabled** — the actual
   blocker was never IAM. Operator re-enabled billing; Secret Manager listing confirmed.
4. All three e2es run sequentially with the runbook's mandatory `--cloud-run-auth-audience`
   + `--cloud-run-auth-impersonate-service-account` flags against the private Cloud Run
   collector `arhugula-r421-otel-collector` (us-central1).
5. Grant REVOKED at close (SA policy bindings back to empty) and the non-gitignored
   `harness.managed-cloud.e2b.toml` copy deleted, per the runbook close discipline.

## Evidence

| e2e | verdict | trace_id (Cloud Trace, observed by polling) | key facts |
|---|---|---|---|
| `r421-managed-cloud-live-e2e` | PASS | `45c26c0ae43996c48043774c40a048bf` | hosted E2B sandbox created + deterministic command; spans `r421.managed_cloud.root`, `sandbox.violation`; managed-otlp-export=true; hosted-provider-calls=1 |
| `r810-files-live-e2e` | PASS | `a1e31e0957cb8c2b784c10180232020b` | real Anthropic Files upload/reference/delete of `file_011CdYvTt3GqdNjSC1Xak4ia` (153 B, sentinel confirmed in response); batch composition `r810-files-live`; span `files.operation` with attrs observed; file deleted |
| `r820-managed-agents-live-e2e` | PASS | `8edd1e4f3c1c4d57d3f831f0e386ad59` | disposable Managed Agents agent+environment+session `sesn_01XeoNz7QqtzhZ9RzXoHDtwr`; full event lifecycle through `session.status_idle`; runtime 1208 ms / 1.208 billable s; span `managed_agents.runtime` with attrs observed |

Static readiness (`just r421-managed-cloud-readiness … --hosted-sandbox-provider e2b`) was
all-PASS (7/7) before any live call. Cost-bearing actions: 3 hosted-provider calls
(usage-billed), one Anthropic Files round-trip, one Managed Agents session (1.208 billable
seconds), E2B sandbox time. No resources left behind: file deleted, session idle-closed,
sandbox disposed by the tools, grant revoked, TOML removed.

## Standing-gate disposition

The "IAM grant → 3 OTLP e2es" operator unlock carried in `roadmap_status.md` since the
2026-06-10 RC close is **RESOLVED**. Re-running in future needs the same one-command grant
(and billing enabled); the runbook remains the recipe.
