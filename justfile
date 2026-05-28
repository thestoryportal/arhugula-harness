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

# ─── operator-facing CLI smoke ─────────────────────────────────────────────

# One-shot run of a workflow manifest. Example: just run path/to/workflow.yaml
run file:
    uv run harness run {{file}}

# Start the daemon (background MCP server over Unix socket).
daemon:
    uv run harness daemon

# Client-side dispatch into a running daemon. Example: just run-daemon workflow.yaml
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
