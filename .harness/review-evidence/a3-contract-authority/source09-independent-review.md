**Source GO.** I found no blocking findings in the 14-path integrated delta for trial-a3-source-09. Every enumerated spec and plan criterion is supported by source, and is witnessed by tests that Buford ran, with two exceptions where evidence is still pending: criterion 3 (the existing full suites) and criterion 5 (pyright). This is not a formal review pass (the canonical budget stays at 0/5), and it is not clearance, shipping or installed acceptance.

## Bindings
- Snapshot `production-source09-01a10968/review-snapshot-01a109ad/manifest.json` (unit trial-a3-source-09). Baseline is main `993c8381…`; the original head was `47ca58b5…`.
- I read `integrated.diff` in full: 2,746 lines over all 14 paths. I did not recompute its SHA256 (`9fa65aa4…`).
- Six source/test hashes in the manifest match the snapshots I read in earlier passes: `llm_dispatch` `4286ef65…`, `hitl_tool_loop` `971bdaf4…`, `post_tool_effect` `74d0d46a…`, `retry_breaker_fallback` `6f2861d9…`, `retry_fallback_namespace` `0ffc6eae…`, `test_cli_daemon_client` `21f96751…`.
- Laws:Code is the full read retained from earlier this session.

## Source judgment (from reading)
**Fence.**
- Each attempt owns one fence:
  - `ToolEffectFence()` is created per `RuntimeLLMDispatcher.dispatch` call and guards `infer()` (`integrated.diff:198-260`).
  - `infer()` dispatches exactly once (`routing_core_surface.py:360-369`), so a carrier can't be swallowed or re-dispatched inside an attempt.
- **Effect-start points:**
  - The tool dispatcher entry (`diff:161-162`).
  - Ollama served-memory execution (`diff:595-601`).
  - The batch result fold `record(started=any(dispatched))` (`diff:423`).
- **What the guard doesn't wrap:** the audit-signing family, already-wrapped carriers and any `BaseException` (`diff:776-783`). This matches the spec's Exclusions (`Spec v1.134:72-77`).
- **Origin:** the provider call plus parsing of the provider's own reply sit inside `provider_call` on both arms (`diff:371-394`, `542-573`). Tool, memory and capture work stay outside it. This matches Spec `:54-56`.

**Wrapper and breaker (cell 10).**
- The carrier arm comes before `except Exception`; only audit-signing and cancellation clauses precede it (`retry_breaker_fallback.py:1282-1320`). It sets `retry.terminal="post-tool-effect"` and `retry.post_tool_effect.origin`, which is exactly the Spec `:57` requirement.
- **Provider-origin charging:** goes through the same waiver rule and `record_failure` the generic arm uses (`:1499-1529`).
- **Re-arm path:**
  - A waived or non-provider carrier leaves the trial `half_open`.
  - The outer `BaseException` arm then re-arms with the carrier in flight (`:989-1007`, `1531-1587`).
  - The re-arm leaves `fail_count` unchanged and sets `trigger_count` to 0 (`retry_breaker.py:421-460`).
  - This matches the cell-10 table at Spec `:62-67`.

**Ollama arm.**
- **Entry:** requires both the superset and the loop (`diff:285-288`); everything else falls through to the unchanged branches, byte for byte.
- **Projection:** a superset entry without `input_schema` is dropped (`diff:437-456`).
- **Offer membership:** derived from the final wire list after memory injection and collision filtering (`diff:521-530`).
- **Nonce:** one per invocation (`diff:536`).
- **Refusal order:** malformed calls first, then calls outside the offer, both before any assessment (`diff:603-618`).
- **Tools-unsupported:** handled only on turn 0, with the B-83 disposition published before the retry (`diff:547-562`, `635-670`).
- **Bound and correlation:** the bound is 16, and the model sees no call id.
- All of this matches Spec items 1-4.

**CP register.**
- The new row's authority cites `Spec_Harness_Runtime_v1_134.md:57` (`diff:69-76`). In the snapshot spec, `:57` is still the Retry wrapper bullet.
- Counts move to 6 rows, 11 emitted keys and 14 live names (`diff:9,27,37`).
- The "other five" docstring fix is included (`diff:46`).

**Re-prompt residual control.**
- Runs through the real wrapper, dispatcher and loop with real CP/IS wiring (`diff:2667-2732`).
- Asserts the plan's text exactly (`Plan v2.65:87`).

**The two unrelated deltas.**
- **`test_cli_daemon_client.py` (`diff:865-881`):** the caller-witness correction I accepted earlier; its hash still matches.
- **`test_lane_init.sh` (`diff:2733-2745`):**
  - The script runs under `set -uo pipefail` (`:11`).
  - The old line was `env | grep -q '^HARNESS_LANE_ID='`. When `grep -q` exits early, `env` can be killed by SIGPIPE, so the pipeline can report "not exported" when the variable is exported.
  - `printenv HARNESS_LANE_ID >/dev/null` makes the same assertion without that race. It's a test-only fix.
  - Neither delta is A3 scope. Disclose both in the PR.

**Citations.**
- The cited candidate lines resolve at the shipping bytes:
  - `llm_dispatch.py` lines 1456, 1510, 1794-1798, 1877-1881, 3883, 5057, 5085, 5144 and 5152-5166;
  - `hitl_tool_loop.py` lines 210-218, 247-276 and 302;
  - `retry_fallback_namespace.py` lines 257-264, 260-261 and 304;
  - `test_b126…` lines 473 and 487;
  - the test-docstring lines.
- `retry_breaker_fallback.py:1301` still holds, because the comment hunk starts at 1304.

## Tested behavior (Buford's evidence; I didn't run it)
- **Criterion 1:** every listed case is present for its stated providers. Waived and emitter-failure re-arm are Anthropic-only, which the plan allows.
- **Criterion 2:** every listed case is present across `test_ollama_mcp_tool_loop.py` and `test_ollama_final_offer.py`.
- **Criterion 4:** all 22 plan mutations were detected, with named failing tests (`criterion4-01a1097d/validated-summary.json`).
  - That includes `batch-dispatch-fence-removed`, killed by the ambiguous-dispatch and non-provider witnesses.
  - This confirms my earlier note that the two batch survivors are coverage gaps for the residual witness alone, not equivalent mutants.
- **Exact-shipping run:** `just codex-test`, 540 passed (`run-8zxhb_3i`). This is a targeted recipe, not the full suite.

## Missing evidence (not source defects)
- **Criterion 3:** the full existing dispatch, refusal, loop, factory, retry and C-RT-36/38 suites need the full gate. `codex-check` is still running, and its earlier failure was diagnosed as `PATH`-related in the environment, not in source.
- **Criterion 5:** pyright on the touched files has no receipt yet. Ruff and format passed earlier at the same bytes (`run-gwlc9ysu`, `run-3qdstz46`).

## Non-blocking notes (P3, prose)
1. **Stale cell references in neighbouring comments.** They still cite only cells 3 / 6-8 (or 6-9) without cell 10:
   - `retry_breaker_fallback.py:990-994`, `:1540`, `:1557`;
   - `retry_breaker.py:425`;
   - the test comment at `diff:2355` ("cells 6-8").
2. **Docs name `47ca58b5` as the implementation.** That's in `Spec v1.134:3,5,9,83,100`, `Plan v2.65:3` and the authority record. The landing head will differ in `retry_breaker_fallback.py` and the replay test. The cited lines still resolve, but the identity has to be rebound to the landed head at clearance.
3. **Register row has no Proposed marker.** Its authority string (`retry_fallback_namespace.py:260-261`) doesn't say "Proposed", so it depends on v1.134 clearance landing before or together with this source.

## Remaining before clearance and shipping
1. A green full `codex-check` and `codex-closeout` on this exact integrated head, including pyright (criteria 3 and 5).
2. Canonical formal review: 0/5, with the merge-gate lenses.
3. Clearance markers for v1.134 / v2.65, filed only after the review is accepted (`Plan §0.2`), plus rebinding the citations from `47ca` to the landed head.
4. Required PR CI, the unchanged merge door and post-main CI.
5. Installed acceptance: Ollama tool-calling, audit and signing, and C-RT-38.
6. Carry the earlier B-298 draft-row corrections into the shipping arc's tracking.

I ran nothing and wrote nothing. I hold no child processes and no handles.

RELEASED
