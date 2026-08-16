#!/usr/bin/env bash
# Blocking provider-free regression gate for the Codex compatibility layer.

set -euo pipefail

unset ANTHROPIC_API_KEY OPENAI_API_KEY E2B_API_KEY GEMINI_API_KEY GOOGLE_API_KEY
unset GOOGLE_APPLICATION_CREDENTIALS GOOGLE_CLOUD_PROJECT GOOGLE_CLOUD_LOCATION
unset GOOGLE_GENAI_USE_VERTEXAI HARNESS_CODEX_REVIEW_ISOLATED
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/arhugula-uv-cache}"

uv run pytest -q \
  tools/test_ac_claim_precision.py \
  tools/test_agy_review.py \
  tools/test_codex_stop_gate.py \
  tools/test_codex_workflow_parity.py \
  tools/test_codex_worktree_gc.py \
  tools/test_arc_exit_report.py \
  tools/test_mutation_probe.py \
  tools/test_arc_metrics.py \
  tools/test_closure_certification.py \
  tools/test_docs_completeness.py \
  tools/test_graft_reachability.py \
  tools/test_leg_selfcheck.py \
  tools/test_memory_closeout_check.py \
  tools/test_prime_report.py \
  tools/test_managed_cloud_readiness.py \
  tools/test_q4_packaging_gate.py \
  tools/test_r420_self_hosted_local_stack.py \
  tools/test_r421_e2b_live_probe.py \
  tools/test_r421_managed_cloud_live_e2e.py \
  tools/test_r430_tail_keep_collector.py \
  tools/test_r810_files_live_e2e.py \
  tools/test_r820_managed_agents_live_e2e.py \
  tools/test_sandbox_host_readiness.py \
  tools/test_self_hosted_readiness.py \
  tools/test_tools_test_coverage_guard.py

for test_script in tools/hooks/test_*.sh tools/statusline/test_*.sh; do
  bash "$test_script"
done
