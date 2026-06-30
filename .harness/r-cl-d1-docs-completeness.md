# R-CL-D1 Documentation Completeness Matrix

Status: documentation suite ready for operator readthrough.

This matrix is the human-facing evidence surface for `R-CL-D1`. It maps the
requested audiences and public runtime surfaces to the docs authored in this
arc, with the local source files used to ground each claim.

## Audience Coverage

| Audience | Required information | Documentation | Source grounding |
| --- | --- | --- | --- |
| New runtime operator | First successful workflow run | `docs/tutorial-first-workflow.md` | `examples/README.md`, `harness.toml.example`, `justfile`, `harness-runtime/src/harness_runtime/cli/app.py` |
| Daily operator | CLI, daemon, admin, exit codes, config practices | `docs/how-to-operate-runtime.md` | `harness-runtime/src/harness_runtime/cli/app.py`, `harness-runtime/pyproject.toml`, `harness-runtime/src/harness_runtime/admin/inspect.py`, `harness-runtime/src/harness_runtime/admin/shutdown_cli.py` |
| Deployment owner | Packaging, self-hosted readiness, managed-cloud readiness, image targets | `docs/how-to-deploy.md` | `tools/q4_packaging_gate.py`, `deploy/images/README.md`, `deploy/self-hosted-local/README.md`, `deploy/managed-cloud/README.md`, `justfile` |
| Maintainer | Package layout, command/config/workflow reference | `docs/reference.md` | `pyproject.toml`, `harness-runtime/pyproject.toml`, `harness-runtime/src/harness_runtime/types.py`, `harness-runtime/src/harness_runtime/config_source.py`, `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` |
| Architecture reviewer | Axis composition, runtime flow, surfaces, close-track state | `docs/architecture.md` | `harness-runtime/src/harness_runtime/api.py`, `harness-runtime/src/harness_runtime/bootstrap/__init__.py`, `.harness/roadmap_status.md`, `.harness/arc-ledger.yaml` |

## Public Surface Coverage

| Surface | Documentation | Source grounding |
| --- | --- | --- |
| `harness run` one-shot | `docs/tutorial-first-workflow.md`, `docs/how-to-operate-runtime.md`, `docs/reference.md` | `harness-runtime/src/harness_runtime/cli/app.py`, `examples/README.md` |
| `harness daemon` and daemon-client dispatch | `docs/how-to-operate-runtime.md`, `docs/architecture.md` | `harness-runtime/src/harness_runtime/cli/app.py`, `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py` |
| Admin inspection/shutdown | `docs/how-to-operate-runtime.md`, `docs/reference.md` | `harness-runtime/src/harness_runtime/admin/inspect.py`, `harness-runtime/src/harness_runtime/admin/shutdown_cli.py`, `harness-runtime/pyproject.toml` |
| Runtime config | `docs/tutorial-first-workflow.md`, `docs/how-to-operate-runtime.md`, `docs/reference.md` | `harness.toml.example`, `harness-runtime/src/harness_runtime/config_source.py`, `harness-runtime/src/harness_runtime/types.py` |
| Workflow manifest loading | `docs/tutorial-first-workflow.md`, `docs/reference.md` | `examples/minimal.toml`, `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` |
| Self-hosted deployment | `docs/how-to-deploy.md`, `docs/architecture.md` | `deploy/self-hosted-local/README.md`, `tools/self_hosted_readiness.py` |
| Managed-cloud deployment | `docs/how-to-deploy.md`, `docs/architecture.md` | `deploy/managed-cloud/README.md`, `tools/managed_cloud_readiness.py`, `tools/r421_e2b_live_probe.py` |
| Portable image packaging | `docs/how-to-deploy.md`, `docs/reference.md` | `deploy/images/README.md`, `deploy/images/harness-runtime.Dockerfile`, `tools/q4_packaging_gate.py` |
| Closure/roadmap status | `docs/README.md`, `docs/architecture.md` | `.harness/roadmap_status.md`, `.harness/arc-ledger.yaml` |

## Automated Completeness Gate

`just docs-completeness-check` runs `tools/docs_completeness.py --check`.
The gate verifies:

| Predicate | Mechanism |
| --- | --- |
| Required docs exist | `tools/docs_completeness.py` required document inventory. |
| Root README points to docs | Checker requires a `docs/README.md` link in `README.md`. |
| Each required doc is source-grounded | Checker requires a `## Source Grounding` section in each required doc. |
| Evidence matrix exists | Checker requires this `.harness` matrix. |
| Core source paths are cited | Checker checks the matrix for the expected runtime/config/deploy source paths. |
| Local markdown links resolve | Checker validates local links in `README.md`, `docs/*.md`, and this matrix. |

## Operator Readthrough Checklist

- Read `docs/README.md` and confirm the audience map matches the intended D1
  scope.
- Run through `docs/tutorial-first-workflow.md` on a local machine with a valid
  provider credential if a live first-run proof is desired.
- Confirm deployment owners can distinguish static readiness from live,
  usage-billed managed-cloud checks in `docs/how-to-deploy.md`.
- Confirm `docs/reference.md` includes the public commands/config/workflow
  surfaces needed for C1 closure certification.

## External Review Note

Tenant policy blocks sending uncommitted private diffs to external review
surfaces. D1 should therefore use the local/decorrelated substitute review path
unless the repository or tenant policy changes.
