# Release-Candidate Deployment Readiness Runbook

> ## ⚠️ ARC CLOSED — this is a RE-VALIDATION recipe, not a live handoff
>
> **This arc ran to completion on 2026-06-10 with verdict `GO for release candidate`.**
> Closure report: [`.harness/release-candidate-deployment-readiness-report-2026-06-10.md`](./release-candidate-deployment-readiness-report-2026-06-10.md).
> Every RC surface across all three tiers — provider-free, self-hosted (daemon + telemetry +
> multitenant + gVisor sandbox), and managed-cloud (E2B, GCP Secret Manager, Neon, Files API,
> Managed Agents, OTLP→Cloud Trace, S3) — was exercised and passing with zero harness code changes.
>
> The runbook is **retained as the re-validation recipe**: run it when a new deployment failure,
> a stack/credential change, or an operator request calls for another RC pass. §10's "first Claude
> prompt" applies **only to such a re-validation pass** — it is no longer a standing session opener.
> **Forward work derives from the roadmap per root `CLAUDE.md` §12, not from this file.**
>
> Status: process-substrate, not design-substrate. Do not create a second roadmap for this phase
> unless the release-candidate effort grows into multiple durable parallel tracks.
> `.harness/roadmap_status.md` is the canonical status surface (the HTML dashboard this runbook
> originally also named was eliminated 2026-07-14 per root `CLAUDE.md` §12).

## 0. Starting State

State pinned at **2026-07-27**, `main` HEAD `1abfaae3` (`ops: roadmap status refresh post-#1134`):

- Semantic overlay hard gate is clean: **389 nodes, 36/36 CXA seams wired, 0 missing CXA endpoints**.
- Phase 8 substitution accounting is closed. Live ledger is 54/54 `RETIRED` and 54/54 pipeline-advanced.
- Latest retirement batch record: `.harness/phase-7d-retirement-events-batch-57.md`.
- Advisory overlay buckets **measured at this pin** (`1abfaae3`, pre-fix): `code_without_cite` 2 ·
  `contract_without_code` 0 · `unit_without_code` 2 · `substitution_without_carrier` 40 ·
  `cxa_seam_missing_endpoint` 0. The two `code_without_cite` rows are comment-only cite
  formalizations landed in **this re-baseline PR**, taking that bucket to **0** — so the
  post-merge baseline is `code_without_cite` 0 with the other four buckets unchanged.
  Full classification, including the pre-fix/post-fix bucket table and the per-file evidence
  for both cites: `.harness/overlay-advisory-traceability-audit-2026-07-27.md` (the §6 deliverable).
- No canonical R-411/R-412/R-420/R-421/R-430/R-500/R-810/R-820/R-830/R-008/R-CXA-* item should be reopened as implementation work unless a new concrete deployment failure proves a regression.

*Historical note (superseded).* The original authoring pinned `main` at `897a585`
(`ops: roadmap status refresh post-overlay-fix`) with 304 nodes / 31 seams. **`897a585` is no
longer an ancestor of `main`** — repository history was re-created 2026-07-25 (`main`'s root
commit is `d45ce125`). Do not attempt `git` range queries against it.

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

4. If `.harness/roadmap_status.md` drift is only the expected terminating-refresh fixed point, treat it as non-blocking. If drift is substantive, stop and reconcile before any RC work.
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
uv run python tools/substitution_ledger.py --check
uv run python tools/forward_register.py --check

# Both ledger checks run under `uv run`, exactly as CI invokes them
# (.github/workflows/ci.yml). Each loads its YAML source through PyYAML —
# `substitution_ledger.py` imports it at module top, `forward_register.py` lazily
# inside `load()` — so the bare `python3` form fails on a clean machine whose
# system interpreter has no PyYAML.
#
# The tools tests run from the `tools/` working directory, also as CI invokes them:
# `test_substitution_ledger.py` imports its module as a top-level name and fails
# collection from the repo root. Keep the parentheses — an unwrapped `cd tools`
# leaves the shell in `tools/` and the next pasted command resolves under it.
(cd tools && uv run python -m pytest test_substitution_ledger.py semantic_overlay/test_overlay.py -q)
```

*(Removed 2026-07-27: the HTML dashboard was eliminated 2026-07-14 per root `CLAUDE.md` §12 —
`python3 tools/dashboard/generate.py --root .` and `tools/test_dashboard_generate.py` no longer
exist and are no longer gates.)*

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
- Substitution ledger validates; forward-register tally validates.
- `.harness/roadmap_status.md` is at the expected fixed point (or a terminating refresh is owed and noted).
- A release operator can identify required environment variables, cloud resources, local daemons, and cleanup steps from repo docs.

If docs are insufficient, fix the runbook/docs in a focused docs PR before live smoke.

## 4. Phase B: Local/Self-Hosted Deployment Smoke

Goal: prove the local/self-hosted deployment path still works from documented setup.

Preconditions:

- Docker Desktop or equivalent Docker daemon is running.
  **Current state (2026-07-27): the Docker daemon is NOT running** — `docker info` fails. Start
  Docker Desktop before any Phase-B command; this is an operator-machine gate, not a harness gap.
- The operator has copied or prepared the self-hosted config, normally:

```bash
cp deploy/self-hosted-local/harness.selfhosted.local.example.toml harness.selfhosted.local.toml
```

  **Substitute the placeholders.** Both example TOMLs ship
  `/absolute/path/to/arhugula-v2` placeholders (11 occurrences in the self-hosted example, 2 in
  `deploy/managed-cloud/harness.managed-cloud.e2b.example.toml`). Replace every one with the real
  workspace root after copying — `just r420-self-hosted-live-e2e` fails at bootstrap stage 1
  otherwise. (Confirmed 2026-07-28.)

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

**Current state (2026-07-28, re-grounded — supersedes the 2026-07-27 "volume ABSENT" note, which
was STALE): the volume `/Volumes/Development/arhugula-r411/` is MOUNTED**; the VM `r411-gvisor` was
merely in state `Stopped`. A plain `limactl start` sufficed — **no re-mount and no re-provision
were needed**. The 2026-06-10 pass ran R-411 against that VM
(`R411_GVISOR_DOCKER_COMMAND="env LIMA_HOME=/Volumes/Development/arhugula-r411/lima-home limactl
shell r411-gvisor sudo docker"`); the 2026-07-28 re-validation re-ran it the same way and it
PASSED (1 passed, 7.87s). Check the VM's actual state before concluding the substrate is absent —
gVisor is Linux-only and never available on the macOS host, but "not running" ≠ "not provisioned".

**Tier-3 driver requirement (found 2026-07-28).** Phase B's `r420-self-hosted-live-e2e` now needs a
tier-3 execution driver: **C-AS-02 §2.3 row 3 floors any stdio MCP transport at `TIER_3_MICROVM`**
(`harness-as/src/harness_as/sandbox_tier_floor.py`), so the template's `r420-echo` stdio echo
server resolves to tier-3 despite its declared `tier-1-process` and aborts with
`SandboxDriverUnavailableError: resolved tier 'tier-3-microvm'` when no driver is configured. The
2026-06-10 GO pass predates that floor's enforcement at this dispatch path. Close it **config-only**
via the commented `[runtime.mcp_clients.sandbox_driver]` block now shipped in
`deploy/self-hosted-local/harness.selfhosted.local.example.toml` plus the wrapper-script step in
`deploy/self-hosted-local/README.md` § "Tier-3 sandbox driver" (the Lima `r411-gvisor` VM above is
one provisioning option). No harness code change is involved.

Setup the R-420 live e2e needs before it will run: see
`deploy/self-hosted-local/README.md` step 4 (empty `prompts/` + `routing_manifest/` directories;
the template already binds `STATE_LEDGER` to a throwaway scratch **directory** — that path class
resolves to a directory containing `state.jsonl`, and binding it to a file path such as the
repo's real `.harness/state.jsonl` aborts stage 1 with `FileExistsError`).

Acceptance criteria:

- Self-hosted readiness passes before stack mutation.
- Stack starts, shows healthy container status, and is torn down or intentionally left running with operator approval.
- R-420, R-430, and R-500 live e2e commands pass or produce classified environment failures.
- R-411 gVisor smoke passes when the Linux VM/runtime is available; otherwise classify as host unavailable, not harness regression.

*(2026-07-28) `tools/r500_multitenant_selfhosted_live_e2e.py` now computes real
`compute_entry_hash(payload)` values for its fabricated audit entries — its former placeholder
hashes are refused by the write-side content-integrity check at
`harness-runtime/src/harness_runtime/lifecycle/audit_writer.py`.*

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

**Current state (2026-07-27) — two live gates carried over from the 2026-06-10 close:**

- **GCP IAM re-grant needed for the three OTLP e2es.** `roles/iam.serviceAccountTokenCreator`
  (`user:storyportalrobert@gmail.com` on SA `gcp-secret-manager-accessor@project-ba535aa4-…`) was
  deliberately **REVOKED** at the 2026-06-10 close per operator decision. `roles/run.invoker`
  (SA → Cloud Run collector `arhugula-r421-otel-collector`, `us-central1`) was **RETAINED**. A
  re-validation of `r421-managed-cloud-live-e2e` / `r810-files-live-e2e` /
  `r820-managed-agents-live-e2e` therefore needs only the token-creator grant re-applied
  (operator-gated privileged IAM mutation — never apply unilaterally), then revoked again at close.
- **AWS session for `r830` expires.** `just r830-s3-live-e2e` fails on an expired session; the
  operator re-runs **`aws login`** first. *(Corrected 2026-07-28 — `aws sso login --profile r830`,
  as the 2026-06-10 pass used, is stale on this host: the `r830` profile carries only
  `login_session` and no `sso_*` keys, and AWS CLI v2.34's own error text says "reauthenticate
  using `aws login`"; the r830 test docstring already documents `aws login`.)* **Fallback that
  needs no interactive re-auth:** the test supports static keys — override `R830_S3_PROFILE` to
  empty and supply the `AWS_*` keys from the MAIN `.env`. The 2026-07-28 re-validation PASSED this
  way.

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
just r421-managed-cloud-live-e2e harness.managed-cloud.e2b.toml \
  --cloud-run-auth-audience https://arhugula-r421-otel-collector-qsqt4j4y3a-uc.a.run.app \
  --cloud-run-auth-impersonate-service-account gcp-secret-manager-accessor@project-ba535aa4-f08d-46b2-ba6.iam.gserviceaccount.com
just r412-e2b-full-vm-live-e2e
just r810-files-live-e2e harness.managed-cloud.e2b.toml \
  --cloud-run-auth-audience https://arhugula-r421-otel-collector-qsqt4j4y3a-uc.a.run.app \
  --cloud-run-auth-impersonate-service-account gcp-secret-manager-accessor@project-ba535aa4-f08d-46b2-ba6.iam.gserviceaccount.com
just r820-managed-agents-live-e2e harness.managed-cloud.e2b.toml \
  --cloud-run-auth-audience https://arhugula-r421-otel-collector-qsqt4j4y3a-uc.a.run.app \
  --cloud-run-auth-impersonate-service-account gcp-secret-manager-accessor@project-ba535aa4-f08d-46b2-ba6.iam.gserviceaccount.com
just r830-s3-live-e2e
just r830-managed-db-live-e2e
```

The two `--cloud-run-auth-*` flags on the three OTLP e2es are **not optional** for this
workspace's collector: `arhugula-r421-otel-collector` is a private Cloud Run service, so the
export needs an ID token minted for its URL audience by an SA that holds `roles/run.invoker`
(the active gcloud account is a user account, which `gcloud auth print-identity-token
--audiences=` rejects — hence the impersonation flag). Omit them and the run emits
unauthenticated telemetry, then fails at Cloud Trace polling *after* the paid provider and
sandbox work has already been spent. Values above are the literal ones the 2026-06-10 GO run
used (`.harness/release-candidate-deployment-readiness-report-2026-06-10.md` risk #1); they
depend on the `serviceAccountTokenCreator` re-grant flagged above. The readiness, probe, and
`r830` commands do not accept these flags and do not need them.

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

Current advisory classes, re-measured **2026-07-27** at `main` `1abfaae3` (full classification:
`.harness/overlay-advisory-traceability-audit-2026-07-27.md`):

- `code_without_cite`: **0** files (was 14 at the 2026-06-10 handoff; the last 2 were closed by
  comment-only cite formalization at the re-baseline PR).
- `contract_without_code`: **0** contracts — **bucket closed** (was 8: `C-CP-30`, `C-CP-37`,
  `C-CP-43`, `C-CP-49`, `C-CP-50`, `C-IS-11`, `C-OD-3`, `C-RT-28`).
- `unit_without_code`: **2** — `U-MEM-17` (implemented at
  `lifecycle/native_memory_adapter.py`; the unit token is cited only from the tests file, and the
  overlay scans `<pkg>/src/**` only) and `U-RT-00` (the Runtime spec's own authoring unit — no
  code carrier by construction). Both ACCEPTED. This bucket was not enumerated at 2026-06-10.
- `substitution_without_carrier`: **40** rows (was 47) = 31 `SUBSTANTIVE_RETIRED` + 9
  `AUTHORING_ONLY`; both `BOUNDED_RESIDUAL` rows now have direct carriers.
- `cxa_seam_missing_endpoint`: **0** hard findings (over 36 wired seams, up from 31).

Cleanup rules:

- Do not add fake cites.
- A cite may be added only when direct code evidence shows the file implements or materially carries the cited contract/unit/substitution.
- If an advisory finding is expected thinness, document the classification rather than forcing a code cite.
- If a contract-without-code finding proves a real missing implementation, stop and route it as a new roadmap/back-flow item rather than hiding it with a cite.

Recommended deliverable:

- A short `.harness/overlay-advisory-traceability-audit-YYYY-MM-DD.md` classifying each advisory bucket as fixed, accepted, or escalated. Prior deliverables: `2026-06-10` (arc close), `2026-07-27` (re-baseline; current baseline).
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

- ~~Dashboard iteration-2: dependency graph, sparklines, live update mode.~~ **RETIRED /
  SUPERSEDED 2026-07-27** — the HTML dashboard was eliminated 2026-07-14 per root `CLAUDE.md` §12;
  `.harness/roadmap_status.md` is the sole surviving status surface. Not selectable.
- ICM governance methodology adoption/reconciliation.
- CXA-2 durable recovery hardening if a real event-sourced, WAL, reconciler, or engine-native recovery loop is introduced.
- Additional provider or deployment feature development.
- Documentation packaging for external users.

## 9. Conflict and Tension Notes

- No new roadmap is needed. `Project_Roadmap_v1.md` + `.harness/roadmap_status.md` are canonical (the HTML dashboard was eliminated 2026-07-14).
- The RC runbook is an execution checklist and handoff, not a competing status system.
- Closed R-items remain closed unless live RC evidence proves regression.
- Advisory overlay findings are traceability work, not proof of missing implementation.
- `overlay.json` is gitignored and generated on demand. Do not force-add it.
- Do not mix design-substrate amendments with runtime implementation unless a specific back-flow arc is opened.

## 10. Suggested First Claude Prompt — RE-VALIDATION PASSES ONLY

**Not a standing session opener.** The arc closed GO on 2026-06-10 (see the banner at the top of
this file); a normal session derives its next action from the roadmap per root `CLAUDE.md` §12.
Use the prompt below only when the operator has explicitly asked for another RC pass:

```text
Run the SessionStart audit, trust .harness/roadmap_status.md, then read .harness/release-candidate-deployment-readiness-runbook.md. This is a RE-VALIDATION pass of an already-GO-closed arc. Do not reopen closed R-items. Start at the HIL scope gate, then proceed through provider-free readiness before requesting approval for any live deployment smoke.
```
