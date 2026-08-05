#!/usr/bin/env bash
# Blocking provider-free regression gate for the Codex compatibility layer.

set -euo pipefail

unset ANTHROPIC_API_KEY OPENAI_API_KEY E2B_API_KEY GEMINI_API_KEY GOOGLE_API_KEY
unset GOOGLE_APPLICATION_CREDENTIALS GOOGLE_CLOUD_PROJECT GOOGLE_CLOUD_LOCATION
unset GOOGLE_GENAI_USE_VERTEXAI HARNESS_CODEX_REVIEW_ISOLATED
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/arhugula-uv-cache}"

uv run pytest -q \
  tools/test_agy_review.py \
  tools/test_codex_stop_gate.py \
  tools/test_codex_workflow_parity.py \
  tools/test_codex_worktree_gc.py \
  tools/test_arc_exit_report.py \
  tools/test_mutation_probe.py

for test_script in tools/hooks/test_*.sh tools/statusline/test_*.sh; do
  bash "$test_script"
done
