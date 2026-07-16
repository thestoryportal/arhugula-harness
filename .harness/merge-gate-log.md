# merge-gate audit log

Append-only. One entry per gated PR — see `.claude/skills/merge-gate/SKILL.md`.

---

## PR #1030 — fix(as): B-25 resolved — sandbox_tier_floor row-7 self-contradiction (Reading A)
Branch: b-25-sandbox-tier-floor-reading-a · Date: 2026-07-15

**Round 1 (final):**
- Concurrency: APPROVE — every code change in this PR is a docstring/comment correction plus one additive pure-function unit test; zero shared-state, I/O, async, or fence logic touched. `ToolMetadata`/`ToolContract`/`MCPClientConfig` remain frozen models throughout.
- Spec-conformance: APPROVE — verified byte-exact: `ADR-D2.md` is v1.3 with a matching change-note, `Spec_Action_Surface_v1.md` is v1.14, `Implementation_Plan_Action_Surface_v1_6.md` exists and correctly amends U-AS-06 (4 sites, 0 AC-count delta). `tools/forward_register.py --check` clean (47 items, B-25 closed, snapshot/digest match). All 3 clearance markers valid YAML with coherent back-references. Flagged 1 non-blocking Class-3 informational finding: `Spec_Harness_Runtime_v1.md` lines 500 + 4724 still loosely group `is_deterministic_inhouse` with the two genuinely-forcing discriminators in prose (without specifically claiming it gates row 7) — registered for a future doc-hygiene pass, not a defect this PR introduced or is required to fix.
- Test-witness: APPROVE — the new witness test exercises the real production resolver body (no seam/mock), reasoned mutation-probe confirms it would catch a future row-7 gating regression, and the pre-existing `test_converter_stamps_per_server_forcing_discriminators` still asserts `contract.is_deterministic_inhouse is True` at the body level (docstring corrections were not substituted for real coverage).

**Also converged separately:** 3 rounds of out-of-family `just codex-review` — round 1 (real, fixed: the ADR/spec fix landed without a matching Implementation-Plan delta, same category as the B-24 arc — `Implementation_Plan_Action_Surface_v1_6.md` authored), round 2 (2 real findings, fixed: the architect-recommendation memo still framed B-25 as unresolved despite this PR closing it — added a resolution callout; `mcp_client_host_factory.py` + its test still called `is_deterministic_inhouse` a "forcing discriminator"/"Reading-B policy source" — corrected; also fixed a wrong function-name citation in the memo), round 3 (clean — "no introduced, actionable code defect found").

**Resolution provenance:** dyadic C10⊥C4 council convening (run per the fork's own Q3 recommendation) + operator `AskUserQuestion` selecting Reading A from a 4-option synthesis — see `.harness/clearance/adr-d2-v1-3-cleared-2026-07-15.md` for the full record.

**Outcome:** All-approve → merged without HIL per standing CI-green directive.

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

---

## PR #1029 — fix(as+runtime): B-24/B-27 ratify+build; B-25 confirmed genuine operator gate
Branch: b24-b27-fork-ratification-build · Date: 2026-07-15

**Round 1:**
- Concurrency: APPROVE — both touched files (`secret_negative_observation.py`'s dispatch-dict lookup, `cli/app.py`'s exit-code branch/dict) are pure reads of immutable module-level constants or locals produced synchronously within a single CLI invocation; no threading, no shared mutable state, no `asyncio.timeout`/cancellation surface touched, no TOCTOU/fence-key patterns present.
- Spec-conformance: APPROVE — verified spec/plan cites byte-exact against current HEAD (including the ADR-D2 §1.5.1 self-contradiction cited in the B-25 addendum); confirmed X-AL-3 compliance (both built items pair code + design-substrate amendment + clearance marker same-PR; B-25 correctly left `operator_gated`, not silently absorbed); confirmed `.harness/forward-register.yaml` B-24/B-25/B-27 statuses + snapshot tallies reconcile via `tools/forward_register.py --check` + `tools/arc_ledger.py --check`; confirmed the root `CLAUDE.md` Runtime-pointer lag flagged is a genuine pre-existing convention (CP pointer is similarly stale on `main`), not an omission. Flagged 2 real hygiene defects (both fixed before merge, see below): malformed YAML frontmatter in both new clearance markers (unquoted colon+backtick inside a plain-scalar list item broke `yaml.safe_load`); stale "8/8 tests pass" prose left behind by a later commit that added a 9th test.
- Test-witness: APPROVE — both CLI exit-code tests exercise the real Typer entrypoint and would genuinely fail under the relevant mutation (verified by reasoning, no tree edit). Flagged 1 real gap (fixed + mutation-probed before merge, see below): the `_ARRIVAL_SITE_SURFACES.get(..., default=...)` fallback branch in `secret_negative_observation.py` was never exercised by any of the 8 existing tests — a mutation reverting the default back to the pre-fix `STATIC_PROMPT_CACHE_PREFIX` bug would have passed unnoticed.

**Follow-up (same PR, before merge):** added `test_verify_sole_resolution_path_unrecognized_site_defaults_to_manifest` (mutation-probed: reverted the default, confirmed 1 failure / 8 pass, restored, confirmed 9/9 pass); quoted the two clearance markers' offending `reviewer_chain` entries so YAML parses cleanly; refreshed the stale 8/8→9/9 test-count references across the AS plan delta + both register files + the PR body.

**Also converged separately:** 4 rounds of out-of-family `just codex-review` against the code+doc diff — round 1 (real, fixed: dispatch dict missed §5.3's own short-form vocabulary), round 2 (real, fixed: the enum extension needed an AS *plan* delta, not just the spec — X-AL-3 gap), round 3 (real P1, fixed: the spec's own replacement prose falsely claimed engine-native pauses are safely resumable via plain re-invocation), round 4 (P2, declined with grounding — the flagged root-`CLAUDE.md` pointer staleness is a pre-existing, self-documented periodic-batch convention, not introduced by this PR; independently confirmed above by the spec-conformance lens).

**Outcome:** All-approve → merged without HIL per standing CI-green directive.
