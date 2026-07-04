# Harness Runtime Documentation

This is the current operator-facing documentation set for the harness runtime.
It covers first use, day-to-day operation, deployment readiness, API/config
reference, and architecture.

## Audience Map

| Audience | Start here | Outcome |
| --- | --- | --- |
| New runtime operator | [Tutorial: first workflow](tutorial-first-workflow.md) | Run the shipped minimal workflow through `harness run`. |
| Daily operator or workflow author | [How to operate the runtime](how-to-operate-runtime.md) | Use one-shot CLI, daemon mode, admin inspection, and shutdown paths. |
| Deployment owner | [How to deploy](how-to-deploy.md) | Validate self-hosted, managed-cloud, and image packaging surfaces before live runs. |
| Maintainer or reviewer | [Reference](reference.md) and [Architecture](architecture.md) | Check public commands, config fields, workflow shape, package layout, and runtime flow. |
| Memory operator or reviewer | [Memory layer README](memory-layer-readme.md) and [Memory substrate](memory-substrate.md) | Use automatic local memory and review policy, architecture, migration, live gates, and closeout evidence. |
| Closure reviewer | [D1 evidence matrix](../.harness/r-cl-d1-docs-completeness.md) | See audience/surface coverage and the source files grounding each doc claim. |

## Public Surfaces Covered

The docs cover these shipped public surfaces:

| Surface | Documentation |
| --- | --- |
| Runtime CLI | [How to operate the runtime](how-to-operate-runtime.md), [Reference](reference.md) |
| Runtime config | [Tutorial](tutorial-first-workflow.md), [Reference](reference.md) |
| Workflow manifests | [Tutorial](tutorial-first-workflow.md), [Reference](reference.md) |
| Example workflows | [Tutorial](tutorial-first-workflow.md) |
| Self-hosted readiness | [How to deploy](how-to-deploy.md) |
| Managed-cloud readiness | [How to deploy](how-to-deploy.md) |
| Runtime image packaging | [How to deploy](how-to-deploy.md), [Reference](reference.md) |
| Architecture/API | [Architecture](architecture.md), [Reference](reference.md) |
| Memory layer usage | [Memory layer README](memory-layer-readme.md) |
| Memory substrate policy and closeout | [Memory substrate](memory-substrate.md) |

## Source Grounding

This index is grounded in the runtime CLI, config loader, example workflow
guide, deployment runbooks, and close-track dashboard:
`harness-runtime/src/harness_runtime/cli/app.py`,
`harness-runtime/src/harness_runtime/config_source.py`,
`harness-runtime/src/harness_runtime/types.py`, `examples/README.md`,
`harness.toml.example`, `deploy/self-hosted-local/README.md`,
`deploy/managed-cloud/README.md`, `deploy/images/README.md`, and
`.harness/roadmap_status.md`. Memory substrate guidance is grounded in
`docs/memory-layer-readme.md`, `docs/memory-substrate.md`,
`.harness/u-mem-25-memory-closeout-evidence.md`, and
`harness-runtime/src/harness_runtime/memory_verification_suite.py`.
