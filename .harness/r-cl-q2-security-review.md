# R-CL-Q2 Security Review and Threat Model

Status: Q2 close evidence for `.harness/audit/Closure_Gate_v1.md` G2.2.
Date: 2026-06-29
Branch: `codex/r-cl-q2-security-review`
Mode: daily CSO-style local audit, 8/10 confidence gate

## Scope

This review covers the current harness workspace as a local Python/uv runtime
and CI/CD repository. The target is not a public web application; the primary
surfaces are the `harness` CLI/API, the local FastMCP daemon over a Unix
socket, outbound MCP client transports, provider SDK construction,
keyring/managed-secret resolution, audit/redaction telemetry, and GitHub
Actions.

No live webhooks, paid provider calls, credential movement, Docker stack
startup, or global user-skill scan was run. The global-skill phase requires
reading outside the repository and was left out of this repo-bound Q2 arc.

## Attack Surface Map

| Surface | Count / posture | Evidence |
|---|---:|---|
| Public internet endpoints | 0 | No FastAPI/Flask/Django app surface; daemon is bound through `uvicorn.Config(uds=...)` at `harness-runtime/src/harness_runtime/cli/app.py:434`. |
| Local CLI/API entrypoints | 3 scripts | `harness`, `harness-inspect`, `harness-shutdown` in `harness-runtime/pyproject.toml`. |
| Local MCP server | 1 | FastMCP server enables DNS rebinding protection at `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py:267`. |
| Outbound MCP client transports | 3 | `stdio`, `streamable_http`, and `sse` in `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py`. |
| Outbound HITL webhooks | opt-in only | `WebhookDeliveryComposer` hashes the URL for telemetry and POSTs only when configured. |
| CI/CD workflows | 3 | `.github/workflows/ci.yml`, `dashboard-deploy.yml`, `x-al-3-guard.yml`. |
| Containers / IaC | 0 active repo-level configs in the local scan | No Docker/Terraform/K8s files found under the audited depth; live Docker recipes are explicit justfile gates. |
| Secret management | keyring/env fallback, GCP Secret Manager | `ProviderSecretsConfig` forbids secret values in config; resolver backends live in `harness_runtime.config.provider_secrets`. |

## Security Findings

| ID | Severity | Confidence | Status | Category | Finding | Evidence |
|---|---|---:|---|---|---|---|
| Q2-1 | HIGH | 9/10 | FIXED | CI/CD supply chain | GitHub Actions used mutable version tags. A compromised or retargeted action tag could execute attacker code in CI with repository token permissions. | `astral-sh/setup-uv@v5` and first-party `actions/*@vN` were replaced with exact tag SHAs in `.github/workflows/ci.yml`, `.github/workflows/dashboard-deploy.yml`, and `.github/workflows/x-al-3-guard.yml`. Verification: `rg -n "uses:\s+[^#\s]+@(?:v\d+|main|master|latest)" .github/workflows` returns no hits. |
| Q2-2 | MEDIUM | 9/10 | RISK ACCEPTED | Audit integrity | OD audit signatures are typed but currently deterministic placeholders until a deployment-bound signer is wired. This protects shape and hash-chain tests but is not a cryptographic attestation backend. | `sign_audit_entry` documents the HSM/KMS/keystore deferral and returns `audit_signature_value=f"unsigned:{key_id}:{payload.prior_entry_hash}"` at `harness-od/src/harness_od/multi_tenant_trace_separation_and_audit_ledger.py:189` and `:203`. Accepted because the code names the Phase-2 composition-root replacement point; Q2 does not silently claim a live signer. |

No open Q2 security findings remain after the action pinning fix and the
explicit audit-signature residual acceptance.

## Per-Surface Probe Results

| Surface | Result | Evidence |
|---|---|---|
| Sandbox isolation | Passed local static/test surface review. STDIO MCP raises the sandbox floor to at least tier 3, remote L2 trust raises to tier 4, and L0 refuses remote. | `harness-as/src/harness_as/sandbox_tier_floor.py:140` through `:151`; focused tests listed below. |
| Secrets | Passed current-tree scan. Only `.env.example` is tracked; `.env` and `.env.local` are gitignored. Runtime config rejects plaintext secret leaves in TOML. | `git ls-files '.env' '.env.*' '*.env'` returned `.env.example`; secret-prefix scan outside tests returned no active key hits; `RuntimeConfigSource._reject_plaintext_secrets` raises at `harness-runtime/src/harness_runtime/config_source.py:312`. |
| MCP trust | Passed local static/test surface review. Deny-list wins; unknown servers are audited; known servers must satisfy the tier floor. | `harness-cp/src/harness_cp/per_server_trust_evaluator.py:176` through `:235`. |
| Redaction / telemetry leakage | Passed provider-free control review. Tokens do not encode the raw value, attribute key, trace id, or span id; raw mappings stay behind the configured token map. Webhook telemetry uses `webhook.url_hash`, not the URL. | `harness-od/src/harness_od/redaction_tokenizer.py:215` through `:231`; `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:215` through `:217`. |
| Audit integrity | Risk accepted for live signature backend deferral; hash-chain shape remains covered by OD tests. | Finding Q2-2. |
| Supply chain | Fixed CI action pinning. Python lockfile and all workspace pyprojects are tracked. Optional CVE scan skipped because `pip-audit` is not installed. | `git ls-files` showed `uv.lock` plus all eight `pyproject.toml` files; `uv --version` returned `uv 0.11.15`; `command -v pip-audit` returned no path. |
| CI event/input handling | Passed local static review. No `pull_request_target`; PR event values are passed through env vars and shell-quoted by the script. | `.github/workflows/x-al-3-guard.yml:20` through `:24`; `.github/scripts/x-al-3-check.sh:22` through `:45`. |
| Repo-local skill supply chain | Passed repo-local scan. Six repo-local `SKILL.md` files found; no hits for network exfiltration, credential reads, or prompt-injection override phrases. | `.agents/skills/{codex-autonomous-loop,optimize-claude-md,overlay-query,roadmap-continue,self-heal,ship-pr}/SKILL.md`. |

## STRIDE Summary

| Component | Spoofing | Tampering | Repudiation | Information disclosure | Denial of service | Elevation of privilege |
|---|---|---|---|---|---|---|
| GitHub Actions | Action tag spoofing fixed by SHA pins. | Workflow edits still depend on GitHub branch protection and reviewer policy. | CI logs and PR checks provide traceability. | No inline secrets found in workflows. | Normal CI resource exhaustion not reported per daily CSO exclusion. | No `pull_request_target` found. |
| Runtime config/secrets | Provider SDK auth is keyring/GCP-backed, not plaintext config. | TOML secret leaf detection fails closed. | Secret resolution fail classes are typed. | Env fallback exists only for configured local backend. | Keyring/GCP unavailable maps to typed failure. | Tool-time secret fetch enforces allowlist when a tool contract is supplied. |
| MCP server/client | Local server uses DNS rebinding protection and Unix-socket serving. | Client transport policy routes through converter/trust/sandbox floors. | Unknown-server trust decisions are audit-required. | Telemetry carries trust tiers and signatures, not credential values. | Transport failures fail startup/dispatch. | L0 remote trust refuses; L2 remote trust forces stronger sandboxing. |
| Telemetry/audit | URL hashes and redaction tokens reduce direct disclosure. | OD hash-chain shape is verified; live signature is deferred. | Audit writer persists tenant-scoped entries. | Multi-tenant pre-collector redaction remains the strongest tier. | Collector/live backend checks were not run in this local arc. | Cross-tenant read API filters by tenant prefix. |

## Posture Notes

- CODEOWNERS is absent. This was not fixed in this arc because the valid GitHub
  owner/team identifier and branch-protection policy are not knowable from the
  local tree; adding a guessed owner can silently no-op. Recommended follow-up:
  add `.github/CODEOWNERS` for `.github/workflows/*` and `.github/scripts/*`
  once the operator confirms the owning GitHub user/team.
- No `.gitleaks.toml` or `.secretlintrc` exists. The current arc performed a
  local current-tree/history probe, but CI does not yet have a dedicated secret
  scanner lane. Recommended follow-up: add a provider-free secret scan gate in a
  later security-hardening arc.
- `pip-audit` was not installed, so dependency CVE enumeration was skipped.
  This is a skipped tool, not a finding. The repo uses a tracked `uv.lock`.
- Global AI-agent skills/hooks were not scanned because they live outside the
  repository and require explicit permission distinct from this repo-local Q2
  closure.

## Verification Commands

- `just codex-preflight`
- `git ls-files '.env' '.env.*' '*.env'`
- `rg -n "AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-(?:ant|live|proj)-[A-Za-z0-9_-]{12,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----" --glob '!**/tests/**' --glob '!**/integration/**' --glob '!tools/test_*' --glob '!tools/dashboard/roadmap.html' --glob '!*.md' --glob '!*.html' .`
- `rg -n "(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}" .github harness-* tools --glob '!**/tests/**' --glob '!**/integration/**' --glob '!tools/test_*' --glob '!tools/dashboard/roadmap.html' --glob '!*.md' --glob '!*.html'`
- `rg -n "pull_request_target|github\.event\.(issue|pull_request|comment|review|head_commit|inputs|client_payload)|secrets\." .github/workflows .github/scripts`
- `rg -n "uses:\s+[^#\s]+@(?:v\d+|main|master|latest)" .github/workflows`
- `rg -n "verify\s*=\s*False|VERIFY_NONE|InsecureSkipVerify|NODE_TLS_REJECT_UNAUTHORIZED|_create_unverified_context" .`
- `find .agents/skills -maxdepth 2 -type f -name SKILL.md -print`
- `rg -n "curl|wget|fetch|https?://|exfiltrat|ANTHROPIC_API_KEY|OPENAI_API_KEY|process\.env|env\.|IGNORE PREVIOUS|system override|disregard|forget your instructions" .agents/skills --glob 'SKILL.md'`
- `git ls-files 'pyproject.toml' '*/pyproject.toml' 'uv.lock'`
- `command -v pip-audit`
- `uv --version`
- `/usr/bin/python3 tools/dashboard/generate.py --root . --out tools/dashboard/roadmap.html`
- Provider-free focused Q2 lane: 315 passed in 20.20s across secret,
  sandbox, MCP-trust, redaction, audit-ledger, webhook, config, encrypted-memory,
  and Codex context-guard tests.
- Full local gate: `UV_CACHE_DIR=/tmp/arhugula-uv-cache just check` passed after
  an escalated rerun for the localhost bind test: ruff clean, pyright 0 errors,
  and pytest 5132 passed / 10 skipped / 24 deselected / 1 xfailed in 70.50s.

The same verification evidence is recorded in the autonomous loop ledger for
the Q2 close PR.

## Disclaimer

This report is an AI-assisted local security review. It is not a substitute for
a professional security audit or penetration test, and it does not prove the
absence of vulnerabilities. For production systems handling sensitive data,
payments, or regulated PII, use this as a first pass and engage qualified
security reviewers before launch.
