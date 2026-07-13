# Harness Preflight Code Review — 2026-07-12

**Requested by:** operator, as the first task in deployment preflight ("full and comprehensive code review of the entire harness codebase").
**Method:** multi-agent Workflow (operator opted in explicitly after a scope/depth AskUserQuestion), full-depth on `harness-runtime` per operator selection. 26 finder agents (16 covering all production `src/` code across 8 packages, 10 doing lighter test-suite-quality scans) fanned out over balanced file chunks (~5-9K LOC each), followed by adversarial verification (independent skeptic re-reads the actual file, tries to refute) of every `critical`/`high` finding. `medium`/`low` findings are reported as-found, not independently verified — see Scope & Limits.
**Scale:** 862 Python files / ~270K LOC reviewed (all of `harness-core`, `harness-is`, `harness-as`, `harness-cp`, `harness-od`, `harness-cxa`, `harness-runtime`, `tools`, plus a lighter pass over all test suites). 47 agents, 1,177 tool calls, ~7.9M subagent tokens, ~37.5 minutes wall-clock, 0 agent errors.

---

## Summary

| Severity | Count | Status |
|---|---:|---|
| **Critical** | 2 | Adversarially verified — both CONFIRMED real |
| **High (src correctness/security)** | 15 | Adversarially verified — all 15 CONFIRMED real (4 additional high findings were verified and REFUTED — see §5) |
| **High (test-quality)** | 3 | Reported as-found |
| Medium (src) | 22 | Reported as-found, not independently verified |
| Medium (test-quality) | 10 | Reported as-found |
| Low (src) | 5 | Reported as-found |
| Low (test-quality) | 6 | Reported as-found |

**Bottom line for deployment:** the 2 critical findings should block deployment until fixed or explicitly accepted — one is a non-functional cryptographic audit-signature mechanism (silent no-op, MULTI_TENANT_COMPLIANCE tier), the other silently misreports every successfully-completed Anthropic Managed Agents session as FAILED. The 15 confirmed high findings are real, independently-verified defects across correctness, security, and resource-safety — none are showstoppers individually, but several touch pause/resume durability and audit-trail integrity, which are the harness's core reliability guarantees.

---

## 1. CRITICAL findings (2, both confirmed)

### 1.1 F5 audit-entry signing is a no-op — MULTI_TENANT_COMPLIANCE tamper-evidence is fake
**`harness-cp/src/harness_cp/f5_signing_key_resolution.py:147`**

`sign_audit_entry` hardcodes `audit_signature_value=b""` (no cryptographic operation at all) and sets `audit_signature_sha256` to the entry's `prior_event_hash` field — a pre-existing hash-chain link, not a signature over the entry's own content. `verify_audit_entry_signature` never inspects either field; it only checks that the key ID string matches. **A tampered or forged audit entry is indistinguishable from a genuine one at verification time.** This defeats the entire purpose of the F5 mechanism, which exists specifically to provide non-repudiation for the harness's highest compliance tier.

**Recommendation:** block on this for any deployment where `MULTI_TENANT_COMPLIANCE` persona tier is in scope. Either implement real signing (the key material is already resolved and available — only the sign/verify steps are stubbed) or explicitly gate the compliance tier as unavailable until fixed.

### 1.2 Every successful Anthropic Managed Agents session is reported as FAILED
**`harness-runtime/src/harness_runtime/lifecycle/managed_agents.py:122`**

`_status_from_anthropic()`'s status-string lookup table is missing `"completed"`, `"paused"`, `"canceled"`, and `"created"` — only `"idle"`, `"running"`, `"rescheduling"`, `"terminated"` are mapped. Any of the missing statuses (including the normal-completion string) falls through to a `FAILED` default. Every Managed Agents session that completes normally gets misreported as failed; the workflow step errors out even though the vendor session succeeded and was billed. Existing unit tests never catch this because they construct the enum value directly rather than exercising the string→enum translation — only the credential-gated live e2e test would surface it.

**Recommendation:** trivial fix (extend the mapping dict), but block on it — this makes the Managed Agents integration unusable in its current state whenever it actually works.

---

## 2. HIGH findings — src correctness/security (15, all confirmed)

Ordered by chunk/package. Full failure scenarios and verifier rationale are in the raw workflow output; this table gives the actionable summary.

| # | File:line | Package | Summary |
|---|---|---|---|
| 1 | `harness-cxa/src/harness_cxa/cp_audit_conversion.py:108` | CXA | `dispatch:`/`hitl:` audit rows omit `audit.cp.prior_event_hash` that all 6 other producer types include as one of "the 4 common CP-sourced fields" — schema-shape inconsistency for the most common audit-row type. |
| 2 | `harness-cp/src/harness_cp/memory_access_mode.py:163` | CP | Memory-access-mode resolution omits `is_external_cli` even when `external_cli_route` is set, so an external-CLI-routed binding can be granted `STANDARD_MEMORY_TOOLS` — a mode its subprocess-text-dispatch path cannot serve. Memory silently never reaches the model. |
| 3 | `harness-cp/src/harness_cp/pause_resume_protocol.py:636` | CP | Snapshot-hash normalization strips a stale field from the top-level fan-out carrier but not from nested `paused_child_branches[].child_snapshot`, so pre-existing HIERARCHICAL pause snapshots fail resume-time hash validation and are misreported as tamper/corruption rather than a serialization-compat gap. |
| 4 | `harness-cp/src/harness_cp/sibling_ledger_entry_composition.py:149` | CP | `action_id` built via unseparated string concatenation (`f"{parent}{thread}{step}"`) — distinct `(parent, thread, step)` triples can collide (e.g. `("run1","0",23)` and `("run10","2",3)` both yield `"run1023"`), unlike the properly delimited `idempotency_key` two lines below. Violates the IS spec's "unique within the ledger" invariant for `action_id`. |
| 5 | `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:197` | CP | `emit_sub_agent_dispatch_audit` hardcodes the literal string `"sub-agent"` instead of a per-dispatch index its own docstring promises — every sub-agent dispatched from the same parent step in one execution (ORCHESTRATOR_WORKERS, PARALLELIZATION) produces audit entries with an **identical, colliding** `action_id`. |
| 6 | `harness-cp/src/harness_cp/workflow_driver.py:7787` | CP | PARALLELIZATION's `_proceed_branch`/`_cancel_branch` have no `SubAgentChildPausedError` handler (unlike the structurally-parallel ORCHESTRATOR_WORKERS path) — a nested sub-agent pause inside a PARALLELIZATION branch is misclassified as an ordinary failure and its resumable state is permanently discarded. The resume-snapshot carrier (`PeerFanOutResumeState`) doesn't even have a field to hold it. |
| 7 | `harness-is/src/harness_is/chain_verification.py:77` | IS | `verify_chain` never recomputes an entry's own `response_hash` from its content — it only checks that consecutive stored hash fields link up. A tampered `response_hash` on any non-terminal entry goes completely undetected while the chain reports fully `VALID`. The sibling memory-ledger verifier does this check correctly; this one doesn't. |
| 8 | `harness-is/src/harness_is/shadow_git_rollback.py:97` | IS | `rollback_to_checkpoint` reads/rewrites the JSONL ledger file directly via `read_bytes`/`write_bytes` around a `git checkout` subprocess call, without acquiring the module-level write lock that `append_ledger_entry` uses. A concurrent append landing inside that window is silently overwritten and lost. |
| 9 | `harness-od/src/harness_od/multi_tenant_trace_separation_and_audit_ledger.py:238` | OD | `verify_hash_chain_integrity` never recomputes an entry's own `entry_hash` from its payload — only checks that consecutive stored hashes link up. A payload mutated in place (bad migration, bug, compromised writer) with hash fields left untouched passes verification. The sibling `verify_rotation_pairs` in the same file does the recompute-and-compare check correctly. |
| 10 | `harness-runtime/src/harness_runtime/memory_capture.py:529` | Runtime | The durable memory-operation ledger entry (carrying a reference to the record) is appended **before** the actual memory record is written. If the record write then fails, the ledger permanently references a `memory_id` that was never persisted — a dangling reference in an append-only, hash-chained ledger. |
| 11 | `harness-runtime/src/harness_runtime/shutdown.py:306` | Runtime | Despite the docstring's explicit promise ("Bounded by timeout: each step is allotted the remaining budget"), tracer-provider shutdown, per-provider `aclose()`, and MCP-host shutdown are never wrapped in `asyncio.wait_for`/a deadline. A stuck TCP teardown (e.g. black-holing firewall) hangs the whole shutdown indefinitely — operators must SIGKILL. |
| 12 | `harness-runtime/src/harness_runtime/lifecycle/sync_dispatcher_facade.py:204` | Runtime | On a dispatch timeout, `future.result(timeout=...)` stops *waiting* but never calls `future.cancel()` — the real async LLM dispatch (plus its cost/audit-ledger write) keeps running detached after the step is already reported `FAILED`. A retry of the same run can then execute concurrently with the orphaned original: two live LLM calls / two audit writes for the same logical step. |
| 13 | `harness-runtime/src/harness_runtime/lifecycle/e2b_tool_execution_driver.py:116` | Runtime | `call_tool` is declared `async` but performs synchronous blocking E2B SDK network I/O (sandbox creation + command execution) with no `asyncio.to_thread` — every TIER_4_FULL_VM tool dispatch blocks the **entire process event loop** for up to ~90s, starving all other concurrent workflows, HITL retries, MCP health-checks, and OTel export. |
| 14 | `tools/r421_managed_cloud_live_e2e.py:371` | tools | `_wait_for_cloud_trace` treats an **empty** span set as a successful observation instead of continuing to poll — GCP Cloud Trace's documented eventual-consistency behavior (trace shell appears before span data) makes the live e2e report success without ever actually verifying spans reached Cloud Trace. The sibling Managed Agents e2e does this correctly. |
| 15 | `tools/codex_context_guard.py:91` | tools | Secret redaction only matches `NAME=VALUE`-shaped values; a Bearer-token or other non-KV-shaped secret passed via `--command` is written verbatim into a **non-gitignored, actively-committed** ledger file, despite the tool's own help text promising general redaction. |

---

## 3. Confirmed defects with the highest correctness-guarantee blast radius

Read together, three of the confirmed findings share a pattern worth calling out explicitly because they degrade the harness's **core reliability contract** (hash-chained, tamper-evident, resumable state):

- **#7 and #9 above** (`chain_verification.py`, `multi_tenant_trace_separation_and_audit_ledger.py`) both implement hash-chain verification that checks *linkage* (does entry N's `prior_hash` match entry N-1's `hash`) but never checks *content integrity* (does entry N's own stored hash match a fresh recompute of entry N's own content). Both have a sibling function in the same codebase (`memory_operation_ledger.py`'s verifier, `verify_rotation_pairs`) that does the recompute-and-compare correctly — strongly suggesting this is a real, fixable gap rather than intentional scope, and that the fix pattern already exists locally to copy.
- **§1.1** (F5 signing) is the same shape at a higher level: the mechanism whose entire purpose is tamper-evidence performs no actual cryptographic check.

If MULTI_TENANT_COMPLIANCE / audit-trail-as-compliance-record is a deployment requirement, these three findings should be treated as a single remediation arc, not three independent tickets — they're the same architectural gap (verification checks structure, not content) recurring at three layers.

---

## 4. Medium/Low findings (src, unverified — 27)

Not independently adversarially verified (scope decision to bound the review's cost — see §7). Reported as-found by the finder agent; each should get a quick human/agent confirmation read before acting, per this workspace's own `disposition-label-is-a-claim` discipline.

**Medium (22):**

| File:line | Package | Summary |
|---|---|---|
| `harness-as/secret_negative_observation.py:127` | AS | Every violation's `surface` mislabeled as `STATIC_PROMPT_CACHE_PREFIX` regardless of actual arrival site. |
| `harness-as/sandbox_tier_floor.py:54` | AS | `ToolMetadata.is_deterministic_inhouse` threaded through the contract types but never read by `sandbox_tier_floor()` — dead discriminator. |
| `harness-cxa/cp_audit_conversion.py:161` | CXA | `_entry_core_or_default` fabricates an opaque placeholder ref instead of raising when `entry_core` is `None`; downstream code can't tell it apart from a genuine IS-anchored ref. |
| `harness-cxa/cp_audit_conversion.py:152` | CXA | Bool fields rendered via generic `str(value)` → `"True"`/`"False"` instead of the codebase's lowercase convention. |
| `harness-cp/five_axis_composition.py:320` | CP | `verify_rotation_6_steps` hardcodes `succeeded=True` for every step — key-rotation verification always reports complete. |
| `harness-cp/default_downgrade_rule.py:65` | CP | `compute_child_blast_radius_ceiling` always returns `READ_ONLY` regardless of parent tier, contradicting its own docstring and the C-CP-12 disposition table. |
| `harness-is/memory_retrieval_index.py:379` | IS | `_scope_matches`'s None-handling is inverted vs. the equivalent checks elsewhere — globally-scoped records silently excluded from this retrieval path. |
| `harness-is/worktree_isolation.py:117` | IS | Unsynchronized check-then-act on the worktree concurrency cap — race allows exceeding it. |
| `harness-is/state_ledger_write.py:62` | IS | Writer serialization is a `threading.Lock` — doesn't hold across OS processes sharing a worktree's ledger. |
| `harness-od/redaction_span_processor.py:216` | OD | Constructor only rejects a *fully-empty* `redacted_attributes` set at MULTI_TENANT_COMPLIANCE; a non-empty-but-insufficient override silently passes despite the "non-toggleable" doc claim. |
| `harness-runtime/config_source.py:314` | Runtime | Plaintext-secret rejection skips the regex check when a value is a dict and recurses — a secret nested one level below a non-matching key is never flagged. |
| `harness-runtime/config/otel_config.py:74` | Runtime | Namespace-declaration attribute key built assuming a trailing `.` on `namespace_prefix`; one row lacks it, producing a malformed key. |
| `harness-runtime/config/sandbox_defaults.py:266` | Runtime | Per-tool sandbox floor mis-attributes `assigned_tier_reason` when surface-default and per-tool tiers are equal; sibling function guards this case correctly. |
| `harness-runtime/memory_promotion.py:475` | Runtime | Memory record written to canonical store before the audit-ledger append, no rollback on ledger-append failure. |
| `harness-runtime/memory_compaction_safety.py:168` | Runtime | Same write-before-ledger-append pattern for compaction decisions. |
| `harness-runtime/lifecycle/collector_daemon.py:238` | Runtime | `stop()` catches its own `asyncio.CancelledError` without re-raising — silently swallows its own cancellation. |
| `harness-runtime/lifecycle/cost_attribution_tool_dispatch.py:172` | Runtime | Caller-composed `idempotency_key` parameter accepted but never used. |
| `harness-runtime/lifecycle/retry_breaker_fallback.py:941` | Runtime | Full-jitter backoff computed twice with independent random draws — telemetry span records a different delay than what's actually slept. |
| `harness-runtime/lifecycle/memory_tool_filesystem.py:117` | Runtime | Per-path lock keyed by raw string, not canonicalized path — two textually-different paths to the same file bypass the atomicity guarantee. |
| `harness-runtime/lifecycle/retry_breaker_tool.py:223` | Runtime | Same double-computed-delay pattern as the fallback retry breaker — telemetry/actual-delay mismatch. |
| `harness-runtime/lifecycle/docker_tool_execution_driver.py:192` | Runtime | Only `TimeoutError` is caught around subprocess communicate; an external `CancelledError` leaves the Docker subprocess running unsupervised. |
| `tools/arc_ledger.py:214` | tools | `--check` gate's snapshot pin omits `standalone_remaining`/`standalone_total` — status flips on those fields can silently pass the gate. |

**Low (5):** `harness-od/holdout_assertion_scaffold.py:42` (trace-id sanitization collision silently drops the second scaffold), `harness-runtime/admin/inspect.py:313` (`--last-n 0` prints ALL entries due to Python's `list[-0:]` quirk), `harness-runtime/cli/app.py:347` (`paused` status mapped to the same exit code as `failed`), `harness-runtime/lifecycle/native_memory_adapter.py:539` (base64-decode failure indistinguishable from "no content"), `tools/r810_files_live_e2e.py:335` (bare `except Exception` on cleanup hides real failures).

---

## 5. Findings verified and REFUTED (4)

These were flagged by finder agents but the adversarial verifier read the actual code and disproved the claimed blast radius. Kept here for completeness/audit trail — no action needed:

- `harness-cp/material_diff_detection.py:160` — vacuous body confirmed real, but the function is not the resume-time safety gate the finding claimed; it has zero live callers on the actual resume path.
- `harness-runtime/lifecycle/step_blast_radius.py:155` — the missing-`StepKind.MANAGED_AGENTS` premise doesn't reproduce; the function's fallback handling covers it correctly.
- `harness-as/secret_fetch_emission.py:102` — the `prior_entry=None`/discarded-entry observation is accurate but doesn't defeat the hash chain the way the finding claimed once the real call-site architecture is traced.
- `harness-as/sandbox_tier_floor.py:144` — the `mcp_server is None` fallthrough is real but doesn't reach an unsafe state given the actual caller contract.

---

## 6. Test-suite quality findings (19)

Lighter pattern-scan (not full logic review) across all test directories, per the scoping decision in §7. Three **High** findings are the most actionable — each is a genuine untested error-path on a real, already-shipped invariant:

- `harness-is/tests/test_memory_operation_ledger.py` — `MemoryOperationProjectionMismatchError`/`MemoryOperationRedactionEventMismatchError` never triggered anywhere.
- `harness-is/tests/test_memory_retrieval.py` — the `packet_hash`/`selected_refs` cross-consistency model validator is never exercised; retrieval is never called before the derived index has been rebuilt.
- `harness-od/tests/test_redaction_span_processor.py` — `MultiTenantOverrideRefusedError` (raised at MULTI_TENANT_COMPLIANCE with an empty redaction set — directly adjacent to §1.1's compliance-tier concern) is never imported or exercised in this file, confirmed by a repo-wide grep.

**Medium (10)** are mostly two recurring shapes: (a) **vacuous self-hash assertions** — `hash(x) == hash(x)` on a single instance instead of comparing two separately-constructed equal instances (`test_u_cp_72_converter_6_prefix_extension.py`, `test_deferral_envelope.py`, `test_bridging_arc_table.py` [Low], `test_cost_attribution_dashboard_binding.py` [Low], `test_redaction_gradient.py` [Low] — 5 occurrences of the same pattern, worth a single sweep fix); (b) **missing-negative-path** on real constructor/validation error branches across IS, runtime, and tools test files. Full list of 19 is in the raw workflow output (`.harness/harness-preflight-code-review-2026-07-12-raw.json`, referenced below).

**Low (6):** three more vacuous self-hash instances (see above), one `--last-n 0`-adjacent CLI test gap, and one suspicious-skip pair (`test_u_mem_24_live_cli_routes.py` — two tests always `pytest.skip()` unconditionally, meaning they can never pass or fail).

---

## 7. Scope, method, and honest limits

- **Scope decision (stated up front, not silently applied):** production `src/` code across all 8 packages got the full 3-dimension review (correctness/security/simplification) at full depth. Test code (which is *larger* than production code in this repo — ~154K of the ~270K total LOC) got a lighter pattern-scan for specific known anti-patterns (vacuous assertions, test-bypass-as-runtime-truth, missing negative-path coverage, suspicious skips) rather than full logic review. This is a deliberate deployment-preflight prioritization, not an oversight.
- **Verification tier:** every `critical`/`high` **src** finding was adversarially re-verified by an independent agent instructed to try to refute it, reading the actual file before deciding (4 of 21 candidates were refuted this way — see §5). `medium`/`low` src findings and all test-quality findings were **not** independently re-verified, to keep the workflow's total agent count bounded — treat them as a competent first pass, not a confirmed defect list.
- **No live execution:** this is a static/read review. Nothing was run against a live provider, sandbox, or deployment target — several findings (e.g. §1.2, §2 #13) would be most conclusively confirmed by the credential-gated live e2e tests already referenced in the findings themselves.
- **Coverage caveat on `workflow_driver.py`:** this single file is 12,298 lines (the largest single file reviewed) and got one dedicated finder agent rather than a split; the agent was instructed to prioritize the dispatch loop, resume/replay logic, and error handling if full-file coverage wasn't achievable. The one confirmed finding from this file (§2 #6) came from exactly that safety-critical area, which is reassuring but doesn't guarantee full-file coverage.
- **Raw data:** every finding's full failure scenario and full verifier rationale (truncated in this summary for readability) is in the companion file `.harness/harness-preflight-code-review-2026-07-12-raw.json` (untruncated, machine-readable — `srcVerified` / `srcUnverified` / `testFindings` arrays). Also traceable to this session's workflow run `wf_eaa15295-306` journal if deeper per-agent transcript detail is ever needed.

---

## 8. Suggested next step

This review does not include fixes — it's the review artifact. Recommended sequencing for a deployment preflight:

1. **Block on the 2 critical findings** (§1) — fix or explicitly accept-and-document before deploying any surface where MULTI_TENANT_COMPLIANCE or Managed Agents are in scope.
2. **Triage the 15 confirmed high findings** (§2) into fix-now vs. register-as-forward-work, prioritizing #6–#9 (pause/resume and hash-chain integrity — the harness's core reliability guarantees) and #12–#13 (resource/event-loop safety under real load).
3. **Spot-confirm the 22 medium src findings** (§4) — 10-15 minutes of grep-and-read each would upgrade most of these to the same confidence tier as §2 before deciding fix-now vs. defer.
4. **The 3 hash-fields recurring pattern** (§3) is worth fixing as one arc rather than three tickets.
5. **Test-quality Highs** (§6) are cheap, high-value fixes — each is "add one `pytest.raises` for an error branch that already exists in production code."
