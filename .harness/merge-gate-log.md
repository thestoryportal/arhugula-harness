# merge-gate audit log

Append-only. One entry per gated PR — see `.claude/skills/merge-gate/SKILL.md`.

---

## PR #1011 — feat(cp): B-31 resume guard validates paused-child workflow identity
Branch: feat/b31-paused-child-workflow-id-guard · Date: 2026-07-15

**Round 1:**
- Concurrency: APPROVE
- Spec-conformance: APPROVE
- Test-witness: BLOCK — byte-compat drop-when-None strip for `child_workflow_id` had zero test coverage, unlike the `synthesis_step_id` precedent it mirrors.

**Fix applied:** added `test_paused_child_absent_workflow_id_byte_compat_hash`, mutation-probed (confirmed fails when the strip is disabled, restored). Also backfilled `pr: "#PENDING"` → `"#1011"` in forward-register.yaml (spec-conformance round-1 minor note).

**Round 2 (final, cap reached):**
- Concurrency: APPROVE
- Spec-conformance: APPROVE
- Test-witness: APPROVE

**Outcome:** All-approve → merged without HIL per standing CI-green directive.

---

## PR #1019 — fix(rt): B-37 remote MCP streamable-HTTP transport residuals
Branch: b-37-mcp-streamable-http-transport-residuals · Date: 2026-07-15

**Round 1 (final):**
- Concurrency: APPROVE — traced the `httpx.AsyncClient` lifecycle, stage-3a resolver threading (sequential, not concurrent), and confirmed no `asyncio.timeout`/TOCTOU/fence-key surfaces exist in this diff. Noted a pre-existing, unrelated `start()` double-entry TOCTOU as out-of-scope (untouched by this PR).
- Spec-conformance: APPROVE — verified `MCPClientConfig`'s own pre-existing docstring already promised an "auth-secret reference" field this PR fulfills, not invents; confirmed no `design-substrate/**` touched (no X-AL-3 concern); confirmed `.harness/forward-register.yaml` B-37 row status/pr/close_out/snapshot all correct via `tools/forward_register.py --check`; independently re-verified the `streamable_http_client` vs `streamablehttp_client` deprecation-status claim against the live SDK.
- Test-witness: APPROVE, with 2 non-blocking noted gaps (both fail-safe, not exploitable): (1) `auth_present` derivation from built `transport_config`'s `headers` key vs the raw `auth_secret_name` field is extensionally untested (no test constructs a case where they diverge); (2) the send-boundary loopback exemption inside `_http_connection_context` itself (as opposed to the `MCPClientConfig`-layer copy) has no positive-control test proving a loopback+headers URL is accepted, not just that non-loopback is refused.

**Follow-up (same PR, before merge):** added `test_auth_present_derives_from_built_transport_config_not_raw_field` (monkeypatches `_build_transport_config` to return no `headers` despite `auth_secret_name` set, asserting `auth_present` follows the built config) and `test_http_connection_context_accepts_loopback_with_headers` (constructs `MCPClientHost` directly with a loopback + headers `transport_config`, asserts no raise) — both mutation-probed.

**Outcome:** All-approve → merged without HIL per standing CI-green directive. codex-review converged clean after 3 rounds of real findings (timeout regression, connection leak, stdio+auth misconfiguration, plaintext-HTTP credential exposure, HTTP_PROXY env-trust leak) — see PR #1019 commit history for details.
