# Release-Candidate Deployment Readiness Runbook

> Status: Claude Code handoff for the next phase after full harness implementation closure. This is process-substrate, not design-substrate. Do not create a second roadmap or dashboard for this phase unless the release-candidate effort grows into multiple durable parallel tracks. Use `.harness/roadmap_status.md` and `tools/dashboard/roadmap.html` as the canonical status surfaces.

## 0. Starting State

Current handoff state at authoring:

- `main` is pushed to `origin/main` at `897a585` (`ops: roadmap status refresh post-overlay-fix`).
- The prior commit `d4b6b4e` merged the overlay-check fix: stale gitignored `tools/semantic_overlay/overlay.json` artifacts no longer fail `overlay-check`; stale tracked snapshots still fail.
- Root checkout was clean and aligned with `origin/main` at Codex handoff.
- `.harness/roadmap_status.md` intentionally records the expected status-refresh fixed-point lag: dashboard head/hash pin `d4b6b4e`, while repository HEAD is the refresh commit `897a585`.
- Phase 8 substitution accounting is closed. Live ledger is 54/54 `RETIRED` and 54/54 pipeline-advanced.
- Semantic overlay hard gate is clean: 304 nodes, 31/31 CXA seams wired, 0 missing CXA endpoints.
- No canonical R-411/R-412/R-420/R-421/R-430/R-500/R-810/R-820/R-830/R-008/R-CXA-* item should be reopened as implementation work unless a new concrete deployment failure proves a regression.

## 1. Claude Code Startup

At the start of the Claude Code session:

1. Let the SessionStart hook run. If it does not run, manually execute the CLAUDE.md section 12.1 audit.
2. Read `.harness/roadmap_status.md` and this runbook before selecting work.
3. Verify the checkout is current:

```bash
git status --short --branch
git fetch origin
git merge --ff-only origin/main
```

4. If dashboard drift is only the expected terminating-refresh fixed point, treat it as non-blocking. If drift is substantive, stop and reconcile before any RC work.
5. Do not ask whether to reopen closed harness implementation rows. The next phase is release-candidate readiness, live acceptance smoke, traceability cleanup, then optional polish.

## 2. HIL Scope Gate

Before running live calls, paid provider actions, cloud mutations, credential-moving commands, or destructive cleanup, present the operator with this scope gate:

```text
HIL gate: I am about to start the release-candidate deployment-readiness arc.

Recommended order:
1. Provider-free RC readiness gate.
2. Local/self-hosted deployment smoke.
3. Managed-cloud deployment smoke.
4. Advisory overlay traceability cleanup.
5. Closure report and optional-polish menu.

I will not run paid provider calls, cloud mutations, or credential-sensitive live tests until you explicitly approve that specific live smoke batch.
```

If the operator approves all live smoke up front, still announce each live batch immediately before execution with the expected resources and cost class.

## 3. Phase A: Provider-Free RC Readiness Gate

Goal: prove a clean checkout is internally release-candidate ready without live provider calls.

Run:

```bash
just check
just overlay-check
python tools/substitution_ledger.py --check
python3 tools/dashboard/generate.py --root .
uv run pytest tools/semantic_overlay/test_overlay.py tools/test_dashboard_generate.py tools/test_substitution_ledger.py
```

Also audit:

- `README.md`
- `harness.toml.example`
- `deploy/self-hosted-local/README.md`
- `deploy/self-hosted-local/harness.selfhosted.local.example.toml`
- `deploy/managed-cloud/README.md`
- `deploy/managed-cloud/harness.managed-cloud.e2b.example.toml`
- `deploy/managed-cloud/r411-r421-infrastructure-selection.md`

Provider-free acceptance criteria:

- Full local gate is green, or every failure is classified with file/test evidence.
- `overlay-check` has 0 hard findings.
- Substitution ledger validates.
- Dashboard regenerates from source, not hand edits.
- A release operator can identify required environment variables, cloud resources, local daemons, and cleanup steps from repo docs.

If docs are insufficient, fix the runbook/docs in a focused docs PR before live smoke.

## 4. Phase B: Local/Self-Hosted Deployment Smoke

Goal: prove the local/self-hosted deployment path still works from documented setup.

Preconditions:

- Docker Desktop or equivalent Docker daemon is running.
- The operator has copied or prepared the self-hosted config, normally:

```bash
cp deploy/self-hosted-local/harness.selfhosted.local.example.toml harness.selfhosted.local.toml
```

Recommended commands:

```bash
just r420-self-hosted-readiness harness.selfhosted.local.toml
just r420-self-hosted-stack-up
just r420-self-hosted-stack-status
just r420-self-hosted-live-e2e harness.selfhosted.local.toml
just r430-tail-keep-live-e2e harness.selfhosted.local.toml
just r500-multitenant-live-e2e harness.selfhosted.local.toml
just r420-self-hosted-stack-down
```

Sandbox-local smoke:

```bash
just r411-gvisor-live-e2e
```

Use `R411_GVISOR_DOCKER_COMMAND` if targeting the Lima Linux VM rather than the default Docker socket.

Acceptance criteria:

- Self-hosted readiness passes before stack mutation.
- Stack starts, shows healthy container status, and is torn down or intentionally left running with operator approval.
- R-420, R-430, and R-500 live e2e commands pass or produce classified environment failures.
- R-411 gVisor smoke passes when the Linux VM/runtime is available; otherwise classify as host unavailable, not harness regression.

## 5. Phase C: Managed-Cloud Deployment Smoke

Goal: prove the managed-cloud acceptance path still works with operator-approved live resources.

Preconditions:

- Operator explicitly approves this live batch.
- `gcloud` login auth is available for the configured Google Cloud project.
- GCP Secret Manager contains the expected `servicename-secret` entries.
- E2B credentials are available.
- Managed OTLP endpoint is non-loopback and reachable.
- AWS profile/S3 env for R-830 is available if running S3 smoke.
- Neon/PostgreSQL connection string is available if running managed-DB smoke.
- Anthropic/OpenAI/Ollama credentials are available only for the specific approved provider smoke.

Prepare or verify managed config, normally from:

```bash
cp deploy/managed-cloud/harness.managed-cloud.e2b.example.toml harness.managed-cloud.e2b.toml
```

Non-mutating readiness:

```bash
just r421-managed-cloud-readiness harness.managed-cloud.e2b.toml --hosted-sandbox-provider e2b
```

Live smoke commands, each requiring explicit approval:

```bash
just r421-e2b-live-probe
just r421-managed-cloud-live-e2e harness.managed-cloud.e2b.toml --hosted-sandbox-provider e2b
just r412-e2b-full-vm-live-e2e
just r810-files-live-e2e harness.managed-cloud.e2b.toml
just r820-managed-agents-live-e2e harness.managed-cloud.e2b.toml
just r830-s3-live-e2e
just r830-managed-db-live-e2e
```

Provider routing smoke is optional in the RC batch unless the operator asks for it:

```bash
just mvp-r300-cross-family
just mvp-r300-ollama
```

Acceptance criteria:

- Each live command records resources touched, trace IDs or provider IDs returned, cleanup performed, and any cost-bearing action.
- Temporary IAM or token grants are removed unless the operator explicitly wants them retained.
- Live failures are classified as credential/resource/config/provider/harness. Do not patch harness code for an infrastructure failure without direct evidence.

## 6. Phase D: Advisory Overlay Traceability Cleanup

Goal: reduce or classify advisory traceability findings after RC gates. These are not hard implementation gaps by default.

Start with:

```bash
just overlay
just overlay-query --orphans
```

Current known advisory classes at handoff:

- `code_without_cite`: 14 files.
- `contract_without_code`: 8 contracts: `C-CP-30`, `C-CP-37`, `C-CP-43`, `C-CP-49`, `C-CP-50`, `C-IS-11`, `C-OD-3`, `C-RT-28`.
- `substitution_without_carrier`: 47 rows.
- `cxa_seam_missing_endpoint`: 0 hard findings.

Cleanup rules:

- Do not add fake cites.
- A cite may be added only when direct code evidence shows the file implements or materially carries the cited contract/unit/substitution.
- If an advisory finding is expected thinness, document the classification rather than forcing a code cite.
- If a contract-without-code finding proves a real missing implementation, stop and route it as a new roadmap/back-flow item rather than hiding it with a cite.

Recommended deliverable:

- A short `.harness/overlay-advisory-traceability-audit-YYYY-MM-DD.md` classifying each advisory bucket as fixed, accepted, or escalated.
- Focused source/docstring edits only when evidence is direct.
- `just overlay-check` and targeted tests after any source edit.

## 7. Closure Report

At the end of the RC arc, produce a report under `.harness/`, for example:

```text
.harness/release-candidate-deployment-readiness-report-YYYY-MM-DD.md
```

The report must include:

- Git head and branch.
- Commands run and exact outcomes.
- Live calls made.
- Costs incurred or cost class if exact cost is unavailable.
- Credentials/resources touched, by name only, never secret values.
- Cleanup performed.
- Remaining risks.
- Recommendation: deploy, hold, or run another RC pass.
- Optional-polish menu for operator selection.

## 8. Optional-Polish Menu

After the RC report is accepted, present this menu and stop for operator selection:

- Dashboard iteration-2: dependency graph, sparklines, live update mode.
- ICM governance methodology adoption/reconciliation.
- CXA-2 durable recovery hardening if a real event-sourced, WAL, reconciler, or engine-native recovery loop is introduced.
- Additional provider or deployment feature development.
- Documentation packaging for external users.

## 9. Conflict and Tension Notes

- No new roadmap/dashboard is needed now. The existing roadmap and dashboard are canonical.
- The RC runbook is an execution checklist and handoff, not a competing status system.
- Closed R-items remain closed unless live RC evidence proves regression.
- Advisory overlay findings are traceability work, not proof of missing implementation.
- `overlay.json` is gitignored and generated on demand. Do not force-add it.
- Do not mix design-substrate amendments with runtime implementation unless a specific back-flow arc is opened.

## 10. Suggested First Claude Prompt

Use this prompt when starting Claude Code:

```text
Run the SessionStart audit, trust .harness/roadmap_status.md, then read .harness/release-candidate-deployment-readiness-runbook.md. Do not reopen closed R-items. Start the release-candidate deployment-readiness arc at the HIL scope gate, then proceed through provider-free readiness before requesting approval for any live deployment smoke.
```
