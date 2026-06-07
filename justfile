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

# Default recipe: list everything.
default:
    @just --list

# ─── core dev loop ─────────────────────────────────────────────────────────

# Run the full pytest suite (mechanism α only; β/γ skip without credentials).
test:
    uv run pytest

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

# Full pre-merge gate: lint + typecheck + tests.
check: lint typecheck test

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

# ─── semantic overlay (R-IF-112) — spec ↔ code ↔ CXA-seam ↔ substitution ────
# A deterministic, no-LLM overlay over the code graph. The agent-facing reference
# tool: "what code implements C-IS-08", "who cites U-RT-112", "show me the orphans".

# Human-readable counts + orphan report (always fresh from HEAD).
overlay:
    uv run python tools/semantic_overlay/overlay.py summary

# Re-derive + write the committed overlay.json artifact (the dashboard/enrich consumer).
overlay-build:
    uv run python tools/semantic_overlay/overlay.py build

# CI gate: HARD drift = a CXA seam whose producer/consumer symbol no longer resolves,
# or a stale committed overlay.json. Exit 1 on either.
overlay-check:
    uv run python tools/semantic_overlay/overlay.py check

# Agent reference lookup, e.g.: just overlay-query --contract C-IS-08
overlay-query *ARGS:
    uv run python tools/semantic_overlay/overlay.py query {{ARGS}}

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

# Check static readiness for the R-420/R-440 SELF_HOSTED_SERVER deployment gate.
# Non-mutating: does not start the daemon, contact OTLP, or fetch secrets.
self-hosted-readiness *args:
    uv run python tools/self_hosted_readiness.py {{args}}

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

# Headless overnight autonomous runner (U-HK-15). Turns loop mode ON, then re-invokes
# `claude -p` in a BOUNDED loop until a genuine gate (halt marker) or the iteration cap.
# Approvals flow through the U-HK-12 permission guard (no --dangerously-skip-permissions).
# `just loop` runs for real; `just loop --dry-run` exercises the loop without calling claude;
# `just loop --max 10` caps iterations. Review .harness/loop_status.md after a run.
# Custom multi-word prompt: use the env var (just variadic args don't preserve quoting):
#   HARNESS_LOOP_PROMPT="do X then Y" just loop
loop *ARGS:
    bash tools/04-loop/run.sh {{ARGS}}
