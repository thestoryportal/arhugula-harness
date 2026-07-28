# Release-Candidate Deployment-Readiness Report — 2026-07-28 (re-validation pass)

> Closure report for a **re-validation pass** of the already-GO-closed release-candidate arc
> (runbook §7). The arc itself closed `GO for release candidate` on 2026-06-10
> (`.harness/release-candidate-deployment-readiness-report-2026-06-10.md`); this pass re-ran the
> runbook recipe against current `main` after ~7 weeks of harness evolution.
> Process-substrate, mode-agnostic. Operator standing approval covered the free gates, the
> Phase-B live batch, the non-GCP Phase-C paid batch (cents), and branch prune.

## Git head and branch

- Branch: `rc-revalidation-close-2026-07-28` (cut from `main`).
- `main` HEAD at the pass: `ed3a770c` (`ops: roadmap status refresh post-#1140`), which refreshes
  over `c78e9a46` (`feat(runtime): … B-82`, PR #1140 merged during the arc).
- Working tree carries exactly one code change, shipped in this PR: the R-500 script fix
  (`tools/r500_multitenant_selfhosted_live_e2e.py`, see Phase B finding #1). `design-substrate/**`
  untouched; `.harness/roadmap_status.md` untouched (the §12.2 refresh is owed as the follow-on
  terminating-refresh commit, not bundled here).
- Runbook §0 pinned starting state at `1abfaae3`; this pass ran against the later `ed3a770c`.
  Every §0 invariant re-verified below (389 nodes / 36 seams / 54-54 ledger) still holds.

## Phase A — Provider-free RC readiness gate: **GREEN**

| Command | Outcome |
|---|---|
| `just check` | ✅ green. **6782 tests at arc start → 6814 at arc close** (the arc absorbed PR #1140's landings); both runs green. |
| `just overlay-check` | ✅ clean — **389 nodes, 36/36 CXA seams, 0 missing CXA endpoints** (matches the §0 pin exactly). |
| `uv run python tools/substitution_ledger.py --check` | ✅ **54/54 RETIRED, 54/54 pipeline-advanced**. |
| `uv run python tools/forward_register.py --check` | ✅ clean. Register **grew 82 → 85 items** across the session (three new forward registrations from other in-flight work, all schema-valid). |
| `(cd tools && uv run python -m pytest test_substitution_ledger.py semantic_overlay/test_overlay.py -q)` | ✅ **34 passed**. |
| `just r420-self-hosted-readiness harness.selfhosted.local.toml` | ✅ **all static checks PASS**. |
| `just r421-managed-cloud-readiness harness.managed-cloud.e2b.toml --hosted-sandbox-provider e2b` | ✅ **all static checks PASS**. |

Deploy-doc audit (runbook §3 list) performed; two doc gaps found and fixed in this PR — see
"Doc/template fixes landed at this pass".

**Provider-free acceptance: met.**

## Phase B — Local/self-hosted deployment smoke: **3/3 GREEN** (+ R-411 sandbox-local smoke, scoped separately by the runbook), three findings

This is where the pass earned its keep. Both R-500 and R-420 **failed on first run** against
current `main` — neither was an environment flake; each was real drift between a live-e2e /
deploy-template surface and a harness invariant that was tightened after the 2026-06-10 GO pass.

| Command | Outcome |
|---|---|
| `just r430-tail-keep-live-e2e harness.selfhosted.local.toml` | ✅ **PASS, unchanged.** Trigger trace preserved (including the `sandbox.violation` span); non-triggering trace dropped. `cost=0`, hosted-provider-calls=0. No drift. |
| `just r500-multitenant-live-e2e` | ❌ **FAILED first** → **FIXED + STRENGTHENED** → ✅ **PASS.** See finding #1. Post-fix: `tenant-resource-separated=true content-redacted=true audit-ledger-separated=true cost=0 hosted-provider-calls=0`, `tenant_a_audit_entries=2 tenant_b_audit_entries=1`; the IS wrapper chain **and** (newly) each tenant's OD audit chain verified. |
| `just r420-self-hosted-live-e2e harness.selfhosted.local.toml` | ❌ **FAILED first** → **UNBLOCKED (config-only)** → ✅ **PASS**, then **re-run after a span-honesty correction** → ✅ **PASS**. See finding #2 + finding #3. Final: `workflow=r420-self-hosted-tool-echo status=success cost=0 hosted-provider-calls=0`. |
| `just r411-gvisor-live-e2e` (with `R411_GVISOR_DOCKER_COMMAND`) | ✅ **PASS — 1 passed in 7.87s.** See R-411 note. |

Phase B made **0 hosted-provider calls, $0**.

### Finding #1 — R-500 script fabricated audit entries with placeholder hashes (harness-side script defect; FIXED)

First run failed at the audit-ledger leg:

```
audit_entry fails content-integrity before write: stored entry_hash='1111…'
```

**Root cause.** `tools/r500_multitenant_selfhosted_live_e2e.py::_make_audit_entry` fabricated its
proof entries with a caller-supplied placeholder `entry_hash` string. That predates the write-side
content-integrity check now enforced at
`harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:679-691` — a write-side mirror of
the sidecar fold's check, which recomputes `compute_entry_hash(payload)` and refuses to persist an
entry whose stored hash does not match its payload (because such an entry would wedge every
post-restart append when the fold rescans it). **The harness is correct; the live-e2e script was
stale.**

**Fix, part 1 — real content hashes.** `_make_audit_entry` now takes a `seed` (used only for the
entry ref + signature label, preserving per-entry distinctness) and computes
`entry_hash=compute_entry_hash(payload)` from `harness_od.audit_ledger_types`
(`audit_ledger_types.py:139`). Re-run **PASSED** end to end.

**Fix, part 2 — the proof was still overclaiming (out-of-family review, codex round 1).** With
part 1 alone the script printed `audit-ledger-separated=true` and a `VALID` chain, but **neither
claim was backed where it mattered**:

- Both TENANT_A appends took `_make_audit_entry`'s default genesis `prior_hash`, so tenant A's
  audit chain was **genesis→genesis** — a genuinely broken link was indistinguishable from the
  intended shape.
- The only chain verification present (`verify_chain(read_ledger(...))`) verifies the **IS state
  ledger wrapper** chain. The per-tenant **OD `AuditLedgerEntry`** chain — the thing
  "audit-ledger-separated" is about — was **never verified at all**.

Both closed:

1. Entries are now built before appending so TENANT_A's second entry chains onto the first
   (`prior_hash=entry_a1.entry_hash`; `compute_entry_hash` is pure, so entry 1's hash is available
   in time).
2. Added per-tenant OD chain verification over the writer's rehydration surface,
   `read_full_entries_for_tenant`
   (`harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:1256`) → `AuditLedger` →
   `verify_hash_chain_integrity` (`harness-od/.../multi_tenant_trace_separation_and_audit_ledger.py:466`,
   the C-OD-21 §21.2 walk). TENANT_A's 2-entry chain and TENANT_B's 1-entry chain are both checked.
   *Grounding note:* that reader's own docstring warns the raw per-tenant sequence is **not** one
   verifiable chain once independent producer families interleave (families discriminate on the CXA
   §0.3 action-id prefix). This proof appends a **single** family (`r500-entry-ref-*`), so each
   tenant's sequence is exactly one chain and needs no partitioning — recorded in-code so a future
   reader does not generalize the call incorrectly. *Scope note (codex round 7):* production's
   producer-aware verifier (`verify_per_family_chains`) enforces linkage only for
   `audit.redaction_token.*` families — cost/HITL/dispatch families deliberately do not chain — so
   this proof exercises the §21.2 chain PRIMITIVE over a deliberately-chained single-family
   fixture (a primitive-level witness across the rehydration surface), not a claim that production
   enforces linkage for this fixture's family. A more production-faithful variant (a genuine
   redaction-token-family fixture) is a registerable polish item, declined at this pass on
   soundness grounds.

**Live re-run (2026-07-28, stack up, free/local, `cost=0`):**

```
[r500-live] completed: tenant_a_trace_id=4f2e6d2582af704cdb75a6bf4de31dc3 tenant_b_trace_id=e1102f16e9c2474ddbcbb4cf51861cf3 base_rate_a=0.2 base_rate_b=0.2 tenant_a_audit_entries=2 tenant_b_audit_entries=1 tenant-resource-separated=true content-redacted=true audit-ledger-separated=true cost=0 hosted-provider-calls=0
```

**Mutation probe (load-bearing witness).** Green alone does not prove the new check does anything,
so the chaining was deliberately reverted (`entry_a2` back to genesis) and the e2e re-run. It
**FAILED loudly**, as it must:

```
R-500 live e2e failed: tenant r500-tenant-a OD audit chain failed verification: audit-ledger hash chain broken at entry 1: prior_entry_hash='0000…0000' != predecessor entry_hash='f6fbbf902ba8a50976dadcb6a3c616405c0098521441caba8b16fbd9f62ce93e' (C-OD-21 §21.2 / C-IS-10 §10.3)
```

That is exactly the state the **pre-fix** script shipped and reported as `VALID`. The probe was
reverted and the e2e re-run green (output above); no probe residue remains in the tree.

**Classification: harness-adjacent tooling defect, fixed and strengthened. Not a harness
regression** — the production write path was already correct and caught the bad entry loudly,
exactly as designed. The overclaim was in the *proof*, not the product.

### Finding #2 — the self-hosted deploy template's stdio MCP echo server is foreclosed at its declared tier-1 (template drift; UNBLOCKED config-only)

First run failed at dispatch:

```
SandboxDriverUnavailableError: resolved tier 'tier-3-microvm'
```

**Root cause.** `deploy/self-hosted-local/harness.selfhosted.local.example.toml` declares the
`r420-echo` MCP client with `transport = "stdio"` and `default_minimum_tier = "tier-1-process"` /
`default_sandbox_tech = "host-process"`. The **enforced C-AS-02 §2.3 row 3 floor** —
`harness-as/src/harness_as/sandbox_tier_floor.py:143-145`, `if mcp_transport is
MCPTransport.STDIO: return _resolved(_tier_max(SandboxTier.TIER_3_MICROVM, floor))` — floors *any*
stdio MCP transport at `TIER_3_MICROVM` regardless of the declared per-client tier. The template
therefore resolves to tier-3 and then has no tier-3 execution driver configured. **The 2026-06-10
GO pass ran before that floor was enforced at this dispatch path**, which is why R-420 passed then
with the same template.

**Unblock — config-only, zero harness code change.** Two operator-local artifacts:

1. A wrapper script at `.harness/r420-scratch/gvisor-docker.sh` (gitignored):
   `exec env LIMA_HOME=/Volumes/Development/arhugula-r411/lima-home limactl shell r411-gvisor sudo
   docker "$@"`. `SandboxDriverConfig.docker_binary` is exec'd as `argv[0]` with no shell, so the
   multi-word Lima invocation needs a single-file wrapper. Smoke-tested standalone (Lima docker
   server 29.5.3 responding).
2. A `[runtime.mcp_clients.sandbox_driver]` table in the gitignored `harness.selfhosted.local.toml`:
   `image = "alpine:3.20"` (already pulled inside the VM; `runsc` registered there),
   `docker_binary` = the wrapper's absolute path, `network = "none"`, and a `command` that is an
   **honest** stdin-reading `sh` runner — it extracts `tool_args.value` from the request JSON and
   echoes it back in MCP-shaped output, rather than returning a constant. The shell escaping was
   empirically tested on the host `sh` before wiring it in.

Re-run **PASSED**: `workflow=r420-self-hosted-tool-echo status=success cost=0`.

**Evidence line, stated honestly:** R-420 self-hosted live e2e passes at **tier-3 via the Lima
`r411-gvisor` VM + `runsc`, driven by an operator-local wrapper script** — **not** "tier-3 out of
the box". A fresh operator following `deploy/self-hosted-local/README.md` as it stood would have
hit the same `SandboxDriverUnavailableError`. That gap is closed by the template + README changes
landed in this PR (below).

**Classification: deploy-template drift, fixed in docs/template. Not a harness defect** — the floor
is the enforced cleared contract behaving correctly; the shipped example config had not caught up.

### Finding #3 — the tier-3 unblock made the `sandbox.enter` span lie about isolation (found by out-of-family review; FIXED + honest re-run)

Finding #2's unblock was **incomplete, and the incompleteness was a telemetry-honesty defect** — surfaced by codex round 2 against the round-1 template, not by any test.

**Root cause.** The template kept the client entry's `default_sandbox_tech = "host-process"` and `default_sandbox_provider = "host"` alongside the new tier-3 driver. Those two fields are the `sandbox.enter` span labels, and **an explicit operator value survives the floor raise**: `resolve_per_tool_sandbox_defaults` re-derives them from the raised tier *only when they are `None`* (`harness-runtime/src/harness_runtime/config/sandbox_defaults.py:275-282`; the per-tier table is `_TIER_TECH_PROVIDER` at `:61-66`, where `TIER_3_MICROVM → ("gvisor", "runsc")`). The resolved decision flows straight into `SandboxDispatchDecision(tier=…, tech=eff.sandbox_tech, provider=eff.sandbox_provider, …)` in `runtime_tool_dispatcher_factory.py`.

So the tool executed under gVisor `runsc` while its span reported **host-process execution**. Tier was honest; the isolation *labels* were not. For a security-telemetry surface whose stated purpose is recording why isolation was applied, that is the wrong direction to be wrong in.

**Counterfactual witness (the pre-fix config, resolved through the real resolver):**

```
PRE-FIX (what the first r420 run emitted):
  tier= tier-3-microvm | tech= host-process / provider= host
```

**This is recorded, not hidden: the first two passing r420 runs in this arc emitted spans carrying those false `host-process` / `host` labels.** No conclusion in this report rested on them (the pass criterion is workflow status, not span labels), and no telemetry left the machine — the local collector stack was torn down — but the runs are named here so the record is accurate.

**Fix.** Both label keys are now **unset** in the shipped template and in the local config, with the reasoning inline. Unsetting is preferred over hardcoding `"gvisor"` / `"runsc"`: `_TIER_TECH_PROVIDER`'s own comment (`sandbox_defaults.py:53-60`) marks these as **placeholder** labels pending the ADR-D2 §1.7 canonical `sandbox.*` namespace reconciliation, so derivation tracks that future rename while a hardcoded copy in a shipped template would silently drift.

**Post-fix witness, same resolver, same config:**

```
RESOLVED (what the sandbox.enter span carries):
  tier     = tier-3-microvm
  tech     = gvisor
  provider = runsc
  reason   = per-tool-sandbox-floor: echo → tier-3-microvm (C-AS-02 §2.3)
```

**Honest re-run (2026-07-28, stack up, free, `cost=0`):**

```
[r420-live] completed: workflow=r420-self-hosted-tool-echo status=success cost=0 hosted-provider-calls=0
```

Stack torn down after; all three containers and the network confirmed `Removed`.

**Classification: deploy-template defect in this pass's own unblock, fixed before merge.** Not a harness defect — the resolver's explicit-value-wins precedence is correct and deliberate (an operator must be able to override labels); the template was supplying an override it had no business supplying.

### Additional Phase-B environment note — placeholder substitution

**Both** scratch configs (`harness.selfhosted.local.toml`, `harness.managed-cloud.e2b.toml`) as
copied from their examples carry `/absolute/path/to/arhugula-v2` placeholders (11 and 2 occurrences
respectively). These were substituted locally for every run. Unsubstituted, the R-420 live e2e
fails at bootstrap stage 1. The runbook now flags this at the copy step (below).

### R-411 gVisor sandbox smoke

```
R411_GVISOR_DOCKER_COMMAND="env LIMA_HOME=/Volumes/Development/arhugula-r411/lima-home limactl shell r411-gvisor sudo docker" just r411-gvisor-live-e2e
```

✅ **PASS — 1 passed in 7.87s.** TOOL_STEP executed under `runsc`.

**The runbook's §4 "volume ABSENT" current-state note was STALE.** Grounding found
`/Volumes/Development/arhugula-r411/` **mounted**, with the VM merely in state `Stopped` (not
absent, not Broken). A plain `limactl start` sufficed — no re-mount and no re-provision were
needed. The runbook §4 note is corrected and re-dated in this PR.

## Phase C — Managed-cloud deployment smoke: **4/4 GREEN non-GCP; 3 GCP-OTLP e2es NOT RUN (operator-gated)**

| Command | Outcome |
|---|---|
| `just r421-e2b-live-probe` | ✅ **PASS** — `stdout=r421-e2b-ok`; **1 hosted E2B call** (auth → provision → run → teardown). |
| `just r412-e2b-full-vm-live-e2e` | ✅ **PASS** — 1 passed; full-VM sandbox provisioned and torn down. |
| `just r830-managed-db-live-e2e` | ✅ **PASS** — 1 passed; real Neon/PG CRUD on a unique path + cleanup. |
| `just r830-s3-live-e2e` | ✅ **PASS** — via the test's own documented **static-key fallback** (`R830_S3_PROFILE` overridden empty + AWS keys sourced from the MAIN `.env`). See the AWS-auth note. |
| `just r421-managed-cloud-live-e2e …` | ⛔ **NOT RUN** — operator-gated (GCP IAM re-grant). |
| `just r810-files-live-e2e …` | ⛔ **NOT RUN** — operator-gated (GCP IAM re-grant). |
| `just r820-managed-agents-live-e2e …` | ⛔ **NOT RUN** — operator-gated (GCP IAM re-grant). |

### AWS auth — the runbook's `aws sso login` instruction is stale on this host

The `r830` profile's SSO session was expired. `aws sso login --profile r830` is **not** the right
command on this machine: the profile carries only `login_session` (no `sso_*` keys), and this host
runs **AWS CLI v2.34**, whose own error text says *"reauthenticate using `aws login`"* — the newer
`aws login` flow, which the `r830` test's own docstring already documents. Rather than fire an
interactive browser re-auth unilaterally, the pass used the test's documented static-key fallback
(profile forced empty, static keys from `.env`) and **PASSED**. The runbook §5 line is corrected in
this PR.

### The three OTLP e2es — operator-gated, **not attempted**

`r421-managed-cloud-live-e2e`, `r810-files-live-e2e`, and `r820-managed-agents-live-e2e` all
require the `roles/iam.serviceAccountTokenCreator` binding (`user:storyportalrobert@gmail.com` on
SA `gcp-secret-manager-accessor@project-ba535aa4-…`) that was **deliberately REVOKED at the
2026-06-10 close** per operator decision. `roles/run.invoker` (SA → Cloud Run collector
`arhugula-r421-otel-collector`, `us-central1`) is still **RETAINED**, so the re-grant is the only
missing piece.

Applying it is a **privileged IAM mutation**. The agent is **hard-blocked** from it by the
auto-mode permission classifier — this block fires regardless of the recorded standing approval,
which is the correct posture for a credential-scope mutation. The exact re-grant command was
surfaced to the operator (roadmap Round 30) and left for the operator to run.

**Consequence for runbook §5's re-grant/revoke cycle: N/A this pass.** The grant was never applied,
so there is nothing to revoke at this close. Net standing IAM state is **unchanged** from the
2026-06-10 close (only the `run.invoker` binding persists, exactly as that report recorded).

## Phase D — Advisory overlay traceability: **GREEN, zero drift vs the 2026-07-27 baseline**

```
just overlay
just overlay-query --orphans
```

Every bucket matches `.harness/overlay-advisory-traceability-audit-2026-07-27.md` **exactly**:

| Bucket | Count | Disposition |
|---|---|---|
| `code_without_cite` | **0** | closed, holds |
| `contract_without_code` | **0** | bucket closed, holds |
| `unit_without_code` | **2** | ACCEPTED (`U-MEM-17` test-only cite; `U-RT-00` authoring unit) |
| `substitution_without_carrier` | **40** | advisory (31 `SUBSTANTIVE_RETIRED` + 9 `AUTHORING_ONLY`) |
| `cxa_seam_missing_endpoint` | **0** | hard gate clean |

No source edited, nothing escalated. **No new Phase-D deliverable is owed** — the 2026-07-27 audit
remains the current baseline.

## Doc/template fixes landed at this pass

All three findings above were *tooling / documentation / template* drift, so all are closed in-repo rather than
merely narrated:

- `deploy/self-hosted-local/harness.selfhosted.local.example.toml` — a **commented**
  `[runtime.mcp_clients.sandbox_driver]` example block immediately after the `r420-echo` entry,
  explaining the C-AS-02 §2.3 row 3 stdio floor and showing the `image` / `command` /
  `docker_binary` / `network` keys with the generic wrapper-script pattern; plus
  `default_sandbox_tech` / `default_sandbox_provider` commented **out** with the finding-#3
  rationale (they were the false-label carriers).
- `deploy/self-hosted-local/README.md` — a new "Tier-3 sandbox driver" section: the floor, the
  wrapper-script step, the **`runsc`-specifically** daemon requirement (the tier-3 branch always
  builds `GVisorRunscToolRunnerExecutionDriver`, which emits a literal `--runtime runsc` — generic
  tier-3 compatibility is not enough), and the finding-#3 span-label rule.
- `.harness/release-candidate-deployment-readiness-runbook.md` — five targeted de-stales:
  AWS `aws login`, the R-411 volume current-state note, the Phase-B stdio-floor requirement,
  the placeholder-substitution warning at the copy steps, and a note that the R-500 script now
  computes real entry hashes. The GO-closed banner is preserved byte-exact.
- `tools/r500_multitenant_selfhosted_live_e2e.py` — the finding-#1 fix: real content hashes, the
  chained TENANT_A entries, and the new per-tenant OD audit-chain verification.

## Live calls made + cost class

- **E2B**: 2 hosted sandbox lifecycles (one `Sandbox.create()` provision/teardown each for
  `r421-e2b-live-probe` and `r412-e2b-full-vm-live-e2e`) — seconds each, all self-cleaned.
  Usage-billed, **cents**.
- **Neon/PG**: 1 connection + CRUD on a unique path, cleaned up. Negligible.
- **AWS S3**: 1 create/view/update/delete cycle on a unique object key + cleanup. Negligible.
- **Anthropic**: no Files API / Managed Agents calls this pass (those e2es are the operator-gated
  OTLP legs). Incidental free model-list GETs only, via `just check`.
- **GCP**: none (the OTLP legs did not run).
- **Local (Ollama, Docker stack, Lima VM, gVisor)**: $0.

**Total cost class: well under a few US cents.** No sustained or leaked billable resources.

## Credentials / resources touched (names only)

`E2B_API_KEY`, `R830_MANAGED_DB_CONNECTION_STRING`, `R830_S3_BUCKET` / `R830_S3_REGION` /
`R830_S3_PROFILE` (overridden empty) plus the static `AWS_*` keys, all from the MAIN `.env` and
consumed only through `just` recipes; OS keyring item `harness`/`r420_probe_key`; the Lima VM
`r411-gvisor` under `LIMA_HOME=/Volumes/Development/arhugula-r411/lima-home`; local Docker Compose
stack (grafana / otel-collector / tempo); local Ollama daemon.
**No secret values were printed, written, or relocated. No IAM mutation was applied.**

## Cleanup performed

- **Docker self-hosted stack**: brought up and taken **DOWN cleanly, four times** (twice during
  the Phase-B runs, once for the finding-#1 re-validation + mutation probe, once for the finding-#3
  honest r420 re-run). Every teardown confirmed all three containers and the network `Removed`.
- **E2B sandboxes**: context-manager teardown + server-side auto-expiry — none persist.
- **Neon/PG**: r830 deleted its unique path.
- **S3**: r830 deleted its unique object key.
- **IAM**: nothing applied, therefore nothing to revoke. Standing IAM unchanged.
- **Scratch config files** — see the deviation note below.
- **Services deliberately left running at close** (operator convenience, no cost): the Ollama.app
  daemon, the Lima `r411-gvisor` VM, and Docker Desktop. Stop the VM with
  `LIMA_HOME=/Volumes/Development/arhugula-r411/lima-home limactl stop r411-gvisor` if not needed.

### Scratch-file disposition — **deliberate deviation from the Leg-8 remove-at-close convention**

The 2026-06-10 close removed both scratch configs to restore a clean tree. This pass **splits** that:

- ❌ **`harness.managed-cloud.e2b.toml` — DELETED.** It is **not** gitignored, so leaving it risks a
  stray `git add` committing machine-specific paths. Convention applied as written.
- ✅ **`harness.selfhosted.local.toml` + `.harness/r420-scratch/gvisor-docker.sh` — RETAINED.**
  Both are gitignored, so neither can pollute the tree.

**Rationale for the deviation:** the three OTLP e2es remain an **open operator-gated residual**.
When the operator applies the IAM re-grant and runs them, they will want the *working* Phase-B
self-hosted config — including the hard-won `[runtime.mcp_clients.sandbox_driver]` block and its
wrapper script — already in place rather than reconstructed from scratch. Deleting a gitignored
artifact that a pending follow-up run needs would be cleanup theatre. The clean-tree property the
convention protects is fully preserved by the two files' gitignore status. Delete them once the
OTLP legs close.

*(The runbook does not itself mandate deletion — Leg-8/§7 speak to cleanup reporting; the 2026-06-10
report's Cleanup line established the remove-both practice. No runbook text was overridden.)*

## Remaining risks / unblock-asks

1. **The three GCP OTLP e2es are unexercised at this pass (operator-gated).** `r421-managed-cloud`,
   `r810-files`, `r820-managed-agents` all need `roles/iam.serviceAccountTokenCreator` re-granted
   to `user:storyportalrobert@gmail.com` on SA `gcp-secret-manager-accessor@project-ba535aa4-…`.
   The agent is hard-blocked from applying it (auto-mode classifier, correctly). The exact command
   was surfaced to the operator. **These three surfaces PASSED at 2026-06-10** and nothing in this
   pass suggests regression — but they are unproven *at this HEAD*. This is the sole residual.
2. **Deploy-template tier-3 requirement is operator-machine-specific.** The template's new
   commented block shows the pattern, but a tier-3 driver still requires an operator-provisioned
   Linux/gVisor substrate (gVisor is Linux-only; never available on the macOS host directly). The
   README now says so; there is no out-of-the-box tier-3 on a bare macOS checkout.
3. **Branch hygiene — permission-guard inconsistency (reported, not resolved).** Gate (e) pruned
   **3 of 9** stale merged branches via the lease-guarded recipe (`rc-rebaseline-phase-d-reaudit`
   #1135, `b81-ow-material-diff-test-parity-step1` #1118, `grounding-pass-b44-b45-b56-b57-b66`
   #1134 — each verified MERGED then 404-confirmed). The permission guard then **HARD-STOPped the
   identical operation** for the remaining 6 (`b39…`/#1092, `b72…`/#1116, `b78…`/#1117,
   `b81-exclusion…`/#1119, `roadmap-status-refresh-post-1092`/#1093,
   `u-mem-live-gates-and-grounding-drift`/#1136). Inconsistent permit/deny across structurally
   identical shapes — a guard-behavior finding, not a harness finding. Reported for operator
   attention; the 6 branches are merged and harmless if left.
4. **Docker Desktop startup fragility (operator-machine).** Docker Desktop initially failed with a
   `vmnetd`/privileged-port AppleScript repair error; the sudo repair command was surfaced to the
   operator and the daemon came up subsequently. Environment, not harness.
5. **`.harness/roadmap_status.md` refresh is owed** as the follow-on terminating-refresh commit
   after this PR merges (§12.2 / §12.2.1). Not bundled here.

## Recommendation: **deploy** — RC re-validation: **PASS with one operator-gated residual (3 OTLP e2es)**

Every RC surface exercisable without a privileged IAM mutation was exercised and passes at
`ed3a770c`: the provider-free gate (`just check` 6814, overlay 389/36, ledgers 54/54, tools 34);
self-hosted **daemon e2e (R-420)** + telemetry (R-430) + multitenant (R-500) + **gVisor sandbox
(R-411)**; managed-cloud **E2B** (probe + full VM), **Neon managed-DB**, and **S3**; and Phase-D
traceability at zero drift.

**Three live-surface defects were found and closed at this pass, all outside harness production
code** — a stale live-e2e script fabricating placeholder audit hashes (the harness caught it
loudly, as designed), a deploy template that predates the enforced stdio tier-3 floor, and — in
this pass's own unblock for that second one — a template override that made the `sandbox.enter`
span report host execution for a tool running under gVisor. That is precisely the value a
re-validation pass exists to deliver: seven weeks of harness tightening had drifted past two
auxiliary surfaces, neither drift was visible to CI, and the third defect was caught only because
the pass's own output was put through out-of-family review. **Zero harness production code was
changed.**

Two of the three were caught by review rather than by a failing command — worth noting for
calibration: a green live-e2e is a weaker witness than it looks, since both the r500 chain
overclaim and the r420 span-label lie produced perfectly passing runs.

The single residual is the three GCP OTLP e2es, blocked on an operator-owned IAM re-grant. They
passed at the 2026-06-10 GO close, the `run.invoker` half of their auth is still in place, and
nothing in this pass indicates regression — but they are **unproven at this HEAD** and the verdict
says so rather than claiming coverage it does not have.

**Resume recipe for the residual.** This pass **deleted** `harness.managed-cloud.e2b.toml` (see the
scratch-file disposition above), so the follow-up run must recreate it first — mirroring the
runbook §5 copy step:

```bash
cp deploy/managed-cloud/harness.managed-cloud.e2b.example.toml harness.managed-cloud.e2b.toml
```

Then substitute the template's three placeholders:

| Placeholder | Value used this pass |
|---|---|
| `/absolute/path/to/arhugula-v2` (`repository_root`) | `/Users/robertrhu/Projects/arhugula-v2` |
| `your-gcp-project-id-or-number` (`gcp_project_id`) | `project-ba535aa4-f08d-46b2-ba6` |
| `https://collector.vendor.example` (`otlp_endpoint`) | `https://arhugula-r421-otel-collector-qsqt4j4y3a-uc.a.run.app` |

With the config recreated and the IAM re-grant applied, run the three e2es from the runbook §5
command block (**both `--cloud-run-auth-*` flags are required** — omit them and the run burns the
paid provider + sandbox work before failing at Cloud Trace polling), then revoke the token-creator
grant again per the 2026-06-10 disposition and delete the recreated config (it is not gitignored).

**Verdict: deploy-ready, with the 3 OTLP e2es carried as a named operator-gated residual.**

## Optional-polish menu (runbook §8)

- ~~Dashboard iteration-2.~~ **RETIRED / not selectable** (HTML dashboard eliminated 2026-07-14).
- Close the OTLP residual: operator applies the IAM re-grant, agent runs the 3 e2es, agent revokes.
- Investigate the branch-prune permission-guard inconsistency (risk #3) — 3/9 permitted, 6/9
  hard-stopped on structurally identical operations.
- Ship a first-class tier-3 driver provisioning path for `deploy/self-hosted-local/` (beyond the
  commented example + wrapper-script recipe landed here).
- ICM governance methodology adoption/reconciliation.
- CXA-2 durable recovery hardening if a real event-sourced / WAL / reconciler / engine-native
  recovery loop is introduced.
- Additional provider or deployment feature development.
- Documentation packaging for external users.
