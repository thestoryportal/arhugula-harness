# justfile — operator command surface for the H_T workspace.
#
# Recipes that exercise real LLM / multi-process orchestration load secrets
# from a repo-local .env (gitignored). Create it with:
#
#     cp .env.example .env && chmod 600 .env
#     # then edit .env to set ANTHROPIC_API_KEY, etc.
#
# `just --list` to see all recipes.

set dotenv-load := true
set dotenv-required := false
set positional-arguments := true
export UV_CACHE_DIR := env_var_or_default("UV_CACHE_DIR", "/tmp/arhugula-uv-cache")

# Default recipe: list everything.
default:
    @just --list

# ─── core dev loop ─────────────────────────────────────────────────────────

# Run the default provider-free pytest suite, matching CI's blocking test lane.
test:
    env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u E2B_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS -u GOOGLE_CLOUD_PROJECT PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring uv run pytest -m "not e2e"

# Run a single test file or node id. Example: just test-one harness-cp/tests/test_foo.py
test-one *args:
    uv run pytest {{args}}

# Pyright type-check across the workspace.
typecheck:
    uv run pyright

# Ruff lint.
lint:
    uv run ruff check .

# Ruff format.
fmt:
    uv run ruff format .

# Full pre-merge gate: workspace sync + lint + typecheck + docs + provider-free tests.
check: codex-sync lint typecheck docs-completeness-check test

# Codex provider-free pytest lane. Strips live provider env and mirrors CI's non-e2e gate.
codex-test *args:
    env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u E2B_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS -u GOOGLE_CLOUD_PROJECT PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring uv run pytest -m "not e2e" {{args}}

# Synchronize all workspace packages before the Codex PR-ready gate.
codex-sync:
    uv sync --all-packages

# Codex PR-ready local gate without live provider credentials.
codex-check: codex-sync lint typecheck docs-completeness-check
    env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u E2B_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS -u GOOGLE_CLOUD_PROJECT PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring uv run pytest -m "not e2e"

# ─── Codex deterministic context guard ─────────────────────────────────────

# Materialize repo/worktree/roadmap state before substantive Codex work.
codex-preflight:
    /usr/bin/python3 tools/codex_context_guard.py preflight

# Write a deterministic local context checkpoint.
codex-checkpoint label="manual":
    /usr/bin/python3 tools/codex_context_guard.py checkpoint --label {{label}}

# Materialize closeout obligations before final response, commit, or PR.
codex-closeout:
    /usr/bin/python3 tools/codex_context_guard.py checkpoint --label pre-closeout --include-branch-diff
    /usr/bin/python3 tools/codex_context_guard.py closeout --require-fresh-checkpoint --include-branch-diff

# Combined local hard gate for context rot / drift / tracking omissions.
codex-context-check:
    /usr/bin/python3 tools/codex_context_guard.py checkpoint --label local-check --include-branch-diff
    /usr/bin/python3 tools/codex_context_guard.py check --require-fresh-checkpoint --include-branch-diff

# Log a credential-gated unit after all non-credential work is closed.
codex-credential-gate *args:
    /usr/bin/python3 tools/codex_context_guard.py credential-gate {{args}}

# Start the deterministic Codex autonomous loop ledger for this arc.
codex-loop-start arc="manual":
    /usr/bin/python3 tools/codex_loop.py start --arc {{arc}}

# Record one autonomous-loop gate. Example:
# just codex-loop-record --phase red --status failed --command "uv run pytest ..." --evidence "expected assertion"
codex-loop-record *args:
    /usr/bin/python3 tools/codex_loop.py record "$@"

# Show current autonomous-loop gate status.
codex-loop-status:
    /usr/bin/python3 tools/codex_loop.py status

# Fail until worktree, development, PR, CI, merge, main-sync, and worktree-disposition gates are recorded.
codex-loop-check:
    /usr/bin/python3 tools/codex_loop.py check

# Bootstrap a Codex autonomous implementation arc. The agent still performs the
# coding/review steps; this recipe creates the evidence ledger and prints the gate order.
codex-autonomous-arc arc="manual":
    /usr/bin/python3 tools/codex_loop.py start --arc {{arc}}
    /usr/bin/python3 tools/codex_loop.py record --phase worktree_ready --status passed --command "git worktree ready" --evidence "linked worktree confirmed for autonomous arc"
    just codex-preflight
    /usr/bin/python3 tools/codex_loop.py record --phase preflight --status passed --command "just codex-preflight" --evidence "preflight completed and checkpoint written"
    @echo "Next gates: worktree_ready -> preflight -> plan -> red(status=failed) -> implementation -> narrow_verify -> local_gate -> decorrelated_review -> closeout -> commit -> push -> pr_opened -> ci_green -> merged -> post_merge_refresh -> main_synced -> worktree_disposition"

# Dry-run safe stale-worktree cleanup. Use --reap to remove only clean merged candidates.
codex-worktree-gc *args:
    /usr/bin/python3 tools/codex_worktree_gc.py {{args}}

# ─── semantic overlay (R-IF-112) — spec ↔ code ↔ CXA-seam ↔ substitution ────
# A deterministic, no-LLM overlay over the code graph. The agent-facing reference
# tool: "what code implements C-IS-08", "who cites U-RT-112", "show me the orphans".

# Human-readable counts + orphan report (always fresh from HEAD).
overlay:
    uv run python tools/semantic_overlay/overlay.py summary

# Re-derive + write the gitignored overlay.json artifact (the dashboard/enrich consumer).
overlay-build:
    uv run python tools/semantic_overlay/overlay.py build

# CI gate: HARD drift = a CXA seam whose producer/consumer symbol no longer resolves,
# or a stale tracked overlay.json. Exit 1 on either.
overlay-check:
    uv run python tools/semantic_overlay/overlay.py check

# Agent reference lookup, e.g.: just overlay-query --contract C-IS-08
overlay-query *ARGS:
    uv run python tools/semantic_overlay/overlay.py query {{ARGS}}

# ─── closure gate (R-IF-115) — the "harness coding fully closed" predicate ──
# Consolidates R-FS-1 + R-CL-Q1..Q4/D1/C1 must_pass into one report.
# Spec: .harness/audit/Closure_Gate_v1.md. Delegates to arc_ledger / overlay /
# substitution_ledger / roadmap — no new source of truth.
closure-gate:
    uv run python tools/closure_gate.py

# Exit 1 if any AUTOMATABLE Tier-1 predicate fails (manual ones reported only).
closure-gate-check:
    uv run python tools/closure_gate.py --check

# ─── R-CL-Q1 structured review artifact gate ────────────────────────────────
# Provider-free checker for the Q1 review/simplification evidence artifact.
q1-review-check report:
    @uv run python tools/q1_review_gate.py --check {{report}}

q1-review-schema:
    @uv run python tools/q1_review_gate.py --schema

# ─── R-CL-D1 documentation suite gate ──────────────────────────────────────
# Provider-free checker for the operator-facing docs suite and grounding matrix.
docs-completeness-check:
    uv run python tools/docs_completeness.py --check

# ─── operator-facing CLI smoke ─────────────────────────────────────────────

# One-shot run of a workflow manifest. Example: just run examples/minimal.toml
# Passes --config harness.toml (create it: cp harness.toml.example harness.toml).
run file:
    uv run harness run {{file}} --config harness.toml

# Start the daemon (background MCP server over Unix socket).
daemon:
    uv run harness daemon --config harness.toml

# Client-side dispatch into a running daemon. Example: just run-daemon workflow.yaml
# (No --config: the running daemon already holds the loaded RuntimeConfig.)
run-daemon file:
    uv run harness run {{file}} --daemon

# ─── mechanism β — real-LLM e2e (env-gated on ANTHROPIC_API_KEY) ───────────
#
# These recipes hard-require ANTHROPIC_API_KEY. The justfile's dotenv-load
# pulls it from .env automatically; if missing, pytest skips the e2e tests
# with a clear cite and the recipe exits cleanly.

_require-anthropic:
    @if [ -z "${ANTHROPIC_API_KEY:-}" ]; then \
        echo "ERROR: ANTHROPIC_API_KEY not set."; \
        echo "  Add it to .env (copy from .env.example) or export it in your shell."; \
        exit 1; \
    fi

# All four mechanism-β e2e tests (AC #1, #3, #7, #8).
mech-beta: _require-anthropic
    uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py \
        -k "real_anthropic or daemon_mode_equivalent or skill_activation or webhook_delivery" \
        -v

# AC #7: SkillActivationHook emits skill.* span under real LLM exercise.
# Advances H_T-AS-8d RETIRE-READY → RETIRED on green.
retire-as-8d: _require-anthropic
    uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py::test_ac7_skill_activation_emits_skill_namespace_span -v

# AC #8: webhook_config delivery emits hitl.webhook.* span under real LLM exercise.
# Advances H_T-OD-5 RETIRE-READY → RETIRED on green.
retire-od-5: _require-anthropic
    uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py::test_ac8_webhook_delivery_emits_hitl_webhook_span -v

# AC #1: single-step real-Anthropic inference round-trip.
mech-beta-ac1: _require-anthropic
    uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py::test_ac1_real_anthropic_single_step_succeeds -v

# AC #3: daemon-mode equivalence to one-shot under real LLM.
mech-beta-ac3: _require-anthropic
    uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py::test_ac3_daemon_mode_equivalent_to_one_shot_with_real_llm -v

# R-100 live e2e: real 3-step INFERENCE workflow against Anthropic (claude-haiku-4-5)
# through api.run (AC #1 + #3 + #4). Paid (~a few cents). live-green is the operator's run.
mvp-r100-real: _require-anthropic
    uv run pytest harness-runtime/tests/integration/test_r100_real_workflow_e2e.py -v

# Requires OPENAI_API_KEY (dotenv-loaded from .env), same shape as _require-anthropic.
_require-openai:
    @if [ -z "${OPENAI_API_KEY:-}" ]; then \
        echo "ERROR: OPENAI_API_KEY not set."; \
        echo "  Add it to .env (copy from .env.example) or export it in your shell."; \
        exit 1; \
    fi

# R-300 (B-2) live cross-family fallback: primary anthropic invalid-model -> real
# openai (gpt-4o-mini) through api.run. Proves the production RetryBreakerFallback
# dispatcher advances across provider families to a real second provider. Paid
# (~a few cents on openai; the 3 anthropic 404 attempts are unbilled). The
# deterministic counterpart (no creds) runs in CI; this is the live confirmation.
mvp-r300-cross-family: _require-anthropic _require-openai
    uv run pytest harness-runtime/tests/integration/test_r300_cross_family_fallback_e2e.py::test_r300_live_cross_family_fallback_against_real_providers -v

# R-300 (B-2) live OLLAMA exercise: same-family ollama fallback (invalid-model ->
# llama3.2:3b) through api.run, exercising the local-open-weight provider end to
# end. FREE — zero-token, zero-secret (local ollama daemon at 127.0.0.1:11434;
# `ollama list` auto-starts it). Skips cleanly if the daemon is unreachable. No
# key required (anthropic + openai degrade-optional).
mvp-r300-ollama:
    uv run pytest harness-runtime/tests/integration/test_r300_cross_family_fallback_e2e.py::test_r300_live_ollama_provider_fallback_exercise -v

# R-CL-P3 live multi-tier e2e: a full `api.run` workflow (echo-MCP TOOL_STEP +
# live-Ollama INFERENCE_STEP) exercised under each of the three bridging-arc
# persona tiers (SOLO / TEAM_BINDING / MULTI_TENANT). Proves the workflow
# completes against a real provider under every tier AND that config.persona_tier
# threads through the bootstrap to the bound §10.3 sampler base-rate (1.0/0.1/0.2),
# observed on the live run path. FREE — zero-token, zero-secret (local ollama
# daemon at 127.0.0.1:11434; llama3.2:3b). Skips cleanly if the daemon is
# unreachable. Closes capability-completion inventory item #8 (P3 live multi-tier).
mvp-r-cl-p3-multi-tier:
    uv run pytest harness-runtime/tests/integration/test_r_cl_p3_live_multi_tier_e2e.py -v

# R-CL-P3 redaction collector-boundary e2e: MULTI_TENANT pre-collector content
# redaction proven through the live R-420 collector → Tempo round-trip — a span
# carrying content sentinels is stripped by the production-materialized
# RedactionSpanProcessor before the BatchSpanProcessor exports, so content never
# reaches Tempo, while a structure attribute survives (selective redaction).
# DOCKER-gated — requires the R-420 stack up (just r420-self-hosted-stack-up); no
# provider inference, no secrets, no paid calls. Skips cleanly if the collector +
# Tempo ports are unreachable. Closes capability-completion inventory item #9
# (P3 redaction collector-boundary proof).
mvp-r-cl-p3-redaction-collector:
    uv run pytest harness-runtime/tests/integration/test_r_cl_p3_redaction_collector_live_e2e.py -v -m e2e

# ─── mechanism γ — multi-process orchestration (currently deferred) ────────
#
# AC #5 (SIGINT drain) + AC #6 (daemon-concurrent two clients) are marked
# @pytest.mark.skip pending per-session ctx isolation. Re-enable when that
# arc lands.

mech-gamma:
    @echo "Mechanism γ is currently deferred-with-cite (per-session ctx isolation)."
    @echo "See harness-runtime/tests/integration/test_track_b_e2e.py:373,385"
    uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py \
        -k "sigint_mid_multi_step or daemon_concurrent" -v --no-header

# ─── housekeeping ──────────────────────────────────────────────────────────

# Show every test marker the suite uses.
markers:
    uv run pytest --markers

# Show currently-skipped tests with reasons.
skips:
    uv run pytest --collect-only -q -rs | grep -E "^SKIP" || echo "(no skips)"

# Check non-mutating host readiness for sandbox/cloud providers.
# Providers: r411-gvisor, r411-kata, r411-shuru, r411-microsandbox, r411-libkrun,
# r412-firecracker, r412-qemu-microvm, r421-e2b.
# Aliases: gvisor, kata, shuru, microsandbox, msb, libkrun, firecracker, qemu-microvm, microvm, e2b.
# Reviewed non-provider: mvm-sh/mvm is a Go bytecode VM, not an isolation sandbox.
sandbox-host-check provider='r411-gvisor':
    /usr/bin/python3 tools/sandbox_host_readiness.py --provider {{provider}}

# Live e2e for R-411 local TIER_3_MICROVM execution via Docker + gVisor/runsc.
# Uses only an already-local Docker image; set R411_GVISOR_DOCKER_COMMAND to
# target a non-default Docker host, e.g. a Lima VM rootful daemon.
r411-gvisor-live-e2e *args:
    uv run pytest harness-runtime/tests/integration/test_r411_gvisor_tool_execution_e2e.py -q {{args}}

# Live R-412 managed full-VM e2e. Requires E2B_API_KEY and creates one
# usage-billed E2B sandbox with outbound internet disabled.
# Codex must get explicit operator approval before running this command.
r412-e2b-full-vm-live-e2e *args:
    uv run --with e2b --package harness-runtime pytest harness-runtime/tests/integration/test_r412_e2b_full_vm_tool_execution_e2e.py -q {{args}}

# Check static readiness for the R-420/R-440 SELF_HOSTED_SERVER deployment gate.
# Non-mutating: does not start the daemon, contact OTLP, or fetch secrets.
self-hosted-readiness *args:
    uv run python tools/self_hosted_readiness.py {{args}}

# Build workspace wheels, export locked third-party requirements, and validate
# the R-CL-Q4 deploy image/readiness artifact surface.
q4-packaging-check:
    uv run python tools/q4_packaging_gate.py --build --check

# Start the local R-420 SELF_HOSTED_SERVER telemetry backend:
# OTel Collector Contrib + Tempo + Grafana. Requires Docker Desktop/daemon.
r420-self-hosted-stack-up:
    docker compose -f deploy/self-hosted-local/compose.yaml up -d

# Stop and remove the local R-420 backend containers/network.
r420-self-hosted-stack-down:
    docker compose -f deploy/self-hosted-local/compose.yaml down

# Show local R-420 backend container status.
r420-self-hosted-stack-status:
    docker compose -f deploy/self-hosted-local/compose.yaml ps

# Static R-420 readiness for a copied self-hosted config. Does not start Docker,
# the daemon, an OTLP probe, a secret fetch, or a provider call.
r420-self-hosted-readiness config:
    uv run python tools/self_hosted_readiness.py --config {{config}}

# Static R-421 MANAGED_CLOUD readiness for an operator-provisioned cloud config.
# Non-mutating: does not start the daemon, probe OTLP, fetch secrets, install
# SDKs, or call managed-cloud/E2B APIs.
r421-managed-cloud-readiness config *args:
    uv run python tools/managed_cloud_readiness.py --config {{config}} {{args}}

# Live R-421 hosted-sandbox candidate probe. Requires E2B_API_KEY and creates a
# usage-billed E2B sandbox. Codex must get explicit operator approval before
# running this command.
r421-e2b-live-probe *args:
    uv run --with e2b python tools/r421_e2b_live_probe.py {{args}}

# Live R-421 managed-cloud e2e. Requires GCP Secret Manager access, a real
# non-loopback managed OTLP endpoint, and creates a usage-billed E2B sandbox.
# Codex must get explicit operator approval before running this command.
r421-managed-cloud-live-e2e config *args:
    uv run --with e2b python tools/r421_managed_cloud_live_e2e.py {{config}} {{args}}

# Live R-420 local e2e. Requires Docker stack up, local Ollama, and keyring
# entries. No hosted-provider inference is performed by the default workflow.
r420-self-hosted-live-e2e config:
    uv run python tools/r420_self_hosted_live_e2e.py {{config}}

# Live R-430 collector proof. Requires the R-420 backend stack running locally.
# Emits no hosted-provider calls; only OTLP/Tempo localhost traffic.
r430-tail-keep-live-e2e config:
    uv run --package harness-runtime python tools/r430_tail_keep_collector_live_e2e.py {{config}}

# Live R-500 multi-tenant self-hosted proof. Requires the R-420 backend stack.
# Emits no hosted-provider calls; only OTLP/Tempo localhost traffic and a temp ledger.
r500-multitenant-live-e2e config:
    uv run --package harness-runtime python tools/r500_multitenant_selfhosted_live_e2e.py {{config}}

# Live R-830 S3 memory backend proof. Requires R830_S3_BUCKET plus ambient
# boto3-compatible AWS/S3 credentials. Performs real S3 create/view/update/delete
# against a unique object key and cleans it up.
r830-s3-live-e2e:
    uv run --with boto3 --with 'botocore[crt]' pytest harness-runtime/tests/integration/test_r830_memory_tool_s3_live_e2e.py -v

# Live R-830 managed-DB memory backend proof. Requires
# R830_MANAGED_DB_CONNECTION_STRING for a PostgreSQL-compatible managed DB.
# Performs real create/view/update/delete against a unique /memories path and
# cleans it up.
r830-managed-db-live-e2e:
    uv run --with 'psycopg[binary]' pytest harness-runtime/tests/integration/test_r830_memory_tool_managed_db_live_e2e.py -v

# Live R-810 Files API proof. Requires ANTHROPIC_API_KEY plus a real
# non-loopback managed OTLP endpoint. Uploads, references, and deletes one
# Anthropic Files API file, then emits files.* telemetry through the managed
# collector. Codex must get explicit operator approval before running this command.
r810-files-live-e2e config *args:
    uv run python tools/r810_files_live_e2e.py {{config}} {{args}}

# Live R-820 Managed Agents proof. Requires ANTHROPIC_API_KEY plus a real
# non-loopback managed OTLP endpoint. Creates one short usage-billed Anthropic
# Managed Agents session and emits managed_agents.* telemetry through the
# managed-cloud collector. Codex must get explicit operator approval before
# running this command.
r820-managed-agents-live-e2e config *args:
    uv run python tools/r820_managed_agents_live_e2e.py {{config}} {{args}}

# ─── operator dashboard (R-XI-01) ──────────────────────────────────────────
#
# Local view of the operator roadmap dashboard. Output goes to the gitignored
# tools/dashboard/public/ (same path CI uses), so it never dirties the tree.
# The hosted copy is live at https://thestoryportal.github.io/arhugula-harness/
# and auto-redeploys on every merge that touches the dashboard sources.

# Regenerate the dashboard from current roadmap state and open it in the browser.
dashboard:
    uv run python tools/dashboard/generate.py --root . --out tools/dashboard/public/index.html
    open tools/dashboard/public/index.html

# Regenerate + serve the dashboard locally on PORT (default 8787) until Ctrl-C.
# Visit http://localhost:PORT/ — re-run this recipe to refresh from current state.
dashboard-serve port='8787':
    uv run python tools/dashboard/generate.py --root . --out tools/dashboard/public/index.html
    @echo "Dashboard at http://localhost:{{port}}/  (Ctrl-C to stop)"
    cd tools/dashboard/public && python3 -m http.server {{port}}

# Run the 4-skill design-elevation loop on a target HTML file (R-XI-02 discipline).
# PAID: spawns a headless `claude` agent per move (sonnet-4-6, ~$0.04/move) that
# invokes the 4 design skills (impeccable / design-taste-frontend / ui-ux-pro-max
# / frontend-design) and authors in-identity variants. dotenv-load supplies the
# Anthropic creds. See dashboard-design/DISCIPLINE.md + live-auto/RUNBOOK.md.
dashboard-elevate file plan:
    node tools/dashboard/live-auto/orchestrator.mjs \
      --file="{{file}}" --plan="{{plan}}" \
      --producer=tools/dashboard/live-auto/producer-skillchain.mjs --no-inject

# ─── out-of-family review — Codex CLI (pilot) ──────────────────────────────
#
# Decorrelated second opinion alongside Claude's advisor(). advisor = Claude
# reviewing Claude = correlated blind spots; Codex (OpenAI, out-of-family) gives
# DECORRELATED errors. The strongest signal is DISAGREEMENT between the two —
# surface that to the operator. See CLAUDE.md §10.9 (pre-merge adversarial gate).
#
# COST: runs on the operator's ChatGPT SUBSCRIPTION, not metered API. The guard
# below verifies "Logged in using ChatGPT" before any call; the flags force
# subscription auth even though dotenv-load injects OPENAI_API_KEY:
#   - `env -u OPENAI_API_KEY` hides the env key from codex
#   - `-c preferred_auth_method="chatgpt"` pins subscription auth
# If the OAuth login is ever absent/stale, the guard FAILS LOUD rather than
# letting codex silently fall back to a metered key. (Codex tool = H_E dev
# tooling, NOT H_T's OpenAI provider, which is metered-API per ADR-F1 / R-300.)

# Guard: refuse to run unless codex is logged in via the ChatGPT subscription.
_require-codex-subscription:
    @if ! command -v codex >/dev/null 2>&1; then \
        echo "ERROR: codex CLI not found on PATH."; exit 1; \
    fi
    @if ! env -u OPENAI_API_KEY codex login status -c preferred_auth_method="chatgpt" 2>&1 | grep -qi "ChatGPT"; then \
        echo "ERROR: codex is not logged in via ChatGPT subscription."; \
        echo "  Run 'codex login' (OAuth) to use the subscription, not metered API."; \
        echo "  (Refusing to run: a stale login could silently bill the API key.)"; \
        exit 1; \
    fi

# Reviewer model = gpt-5.5, set as the default in ~/.codex/config.toml (top-level +
# active profile) per operator direction 2026-06-03. NOTE: `codex review` ignores a
# per-invocation `-c model=` when a profile is active (the profile's model wins), so
# the model is governed by config.toml, not pinned here. The run banner prints the
# effective `model:` — confirm it reads `gpt-5.5`.

# Out-of-family review of the current branch vs BASE (default main), subscription auth.
codex-review base='main': _require-codex-subscription
    env -u OPENAI_API_KEY codex review -c preferred_auth_method="chatgpt" --base {{base}}

# Out-of-family review of staged + unstaged + untracked changes, subscription auth.
codex-review-uncommitted: _require-codex-subscription
    env -u OPENAI_API_KEY codex review -c preferred_auth_method="chatgpt" --uncommitted

# Advisory CodeRabbit review. This is optional and complements, not replaces,
# `just codex-review` and CI. Run after a meaningful diff exists.
_require-coderabbit:
    @if ! command -v coderabbit >/dev/null 2>&1; then \
        echo "ERROR: coderabbit CLI not found."; \
        echo "  Install/authenticate CodeRabbit before using this optional advisory gate."; \
        exit 1; \
    fi
    @if ! coderabbit auth status --agent >/dev/null 2>&1; then \
        echo "ERROR: coderabbit agent auth is not ready."; \
        echo "  Run: coderabbit auth login --agent"; \
        exit 1; \
    fi

coderabbit-review *ARGS: _require-coderabbit
    coderabbit review --agent "$@"

# Headless overnight autonomous runner (U-HK-15). Turns loop mode ON, then re-invokes
# `claude -p` in a BOUNDED loop until a genuine gate (halt marker) or the iteration cap.
# Approvals flow through the U-HK-12 permission guard (no --dangerously-skip-permissions).
# `just loop` runs for real; `just loop --dry-run` exercises the loop without calling claude;
# `just loop --max 10` caps iterations. Review .harness/loop_status.md after a run.
# Custom multi-word prompt: use the env var (just variadic args don't preserve quoting):
#   HARNESS_LOOP_PROMPT="do X then Y" just loop
loop *ARGS:
    bash tools/04-loop/run.sh {{ARGS}}
