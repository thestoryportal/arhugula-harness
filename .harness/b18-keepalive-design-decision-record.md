# B-18-KEEPALIVE — design decision record (pre-build, reviewer-hardened, operator-ratified)

*R-FS-2 Wave 1 arc. Boot-time prompt-cache pre-warm + keep-alive loop (ADR-D3 §1.5 lines 189-190). This DDR is the executable spec for the build — authored at the pre-build design gate (2026-07-11), grok-reviewed (AMEND-THEN-PROCEED), operator-ratified on scope. No code written yet; this is the handoff so the build can be executed cleanly (incl. under a switched model / fresh context).*

**Status:** DESIGN LOCKED — ready to build. Merge needs an operator per-PR AUQ (`[[background-job-git-push-blocked]]`).

---

## 0. Authority + current state

- **ADR-D3 §1.5 lines 189-190** (cleared, byte-verified by grok): `pre_warm: max_tokens=0 at process boot per Cluster 2 V2 §[HIGH] Pattern P1.3; keep-alive every 4min for 5min TTL caches`.
- The **ttl-selection half** (line 188) already shipped: `harness-runtime/src/harness_runtime/lifecycle/cacheable_epoch.py` (`select_cache_ttl`, runtime spec v1.97).
- **This arc = the pre-warm + keep-alive half** (lines 189-190). Zero code today (verified twice: NotebookLM audit + adversarial reviewer). The ADR-D4 §1.8 fan-out cohort warm-up (built through #933) is a *different, sibling* mechanism.
- Deferral lineage: 3c DDR §8 named `B-18-KEEPALIVE (R2)`; `.harness/u1-slice3b-epoch-partition-design.md` §3.3/§4.3 records "C11-safe default when built: opt-in, default off" + R2 = skip-under-cost-ceiling carve-out deferred with the mechanism.
- Register scope: `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §2 "B-18-KEEPALIVE" (6 scope items + acceptance).

---

## 1. Operator-ratified scope decision (2026-07-11 AUQ)

**Boot pre-warm attaches at bootstrap stage 5 (fires for BOTH one-shot `harness run` AND the daemon — every process boot, byte-faithful to ADR "at process boot"). Keep-alive attaches at the daemon only (`_daemon_main`).**

- This is grok's recommended "third reading" (see §3). The alternative I initially proposed (daemon-only for both, one-shot pre-warm deferred) was rejected in favor of ADR byte-faithfulness.
- Consequence of the stage-5 placement (LOAD-BEARING): pre-warm now runs *inside* `run_bootstrap`. It MUST be strictly best-effort — a prewarm failure MUST be caught and MUST NOT propagate as a `BootstrapFailure` (that would abort the whole run/daemon). Wrap the stage-5 prewarm call in a try/except that logs + swallows, mirroring `_attribute_cost_best_effort`'s "observability-not-contract" discipline (`llm_dispatch.py:1577-1578`).
- R2 (skip-under-cost-ceiling) is RE-DEFERRED (see §9). One-shot pre-warm is now BUILT (not deferred), so the earlier "one-shot deferral paragraph" is dropped.

---

## 2. Grok pre-build review — outcome + amendments folded

Full review saved at `/Users/robertrhu/.claude/jobs/7fc6578c/tmp/grok-prebuild-review-out.md` (job-tmp — transcribe key points here since that dir is reap-on-job-delete). Grok (grok-4.5, out-of-family, replaces down-Codex; SuperGrok subscription, $0, X-AL-1 dev tooling) verified every file:line anchor as CORRECT and returned **AMEND-THEN-PROCEED**. The 8 amendments, all folded into this DDR:

1. **Scope** → stage-5 pre-warm (both) + daemon keep-alive. [operator-ratified, §1]
2. **Bare handle (BLOCKING N1):** the wrap chain is `retry(HITL(bare))` — 3 deep (`retry_breaker_fallback.py:295-296`; HITL composed at `stage_5_loop_init.py:472-488`, retry wrap at `:489-515`). `ctx.llm_dispatcher.inner` is the **HITL composer, not bare**. A prewarm routed through the wrapper hits the PRE_ACTION HITL gate that "always fires" at MVP (`hitl_gate_composer.py:58-61`) → **daemon boot hangs on AskUserQuestion**. So `prewarm()` lives on the **bare `RuntimeLLMDispatcher`** and callers reach the bare handle explicitly (§4).
3. **Eligibility gate (N4):** gate on the real non-vacuity floor before any paid call (§4.2), so "eligible" ⟺ "a cache breakpoint is actually placed" ⟺ "the ping warms something."
4. **Lifecycle (Q4/N3):** keep-alive `cancel()` + `await` in a `finally` **before** `await _shutdown(ctx)` (§5).
5. **Honest cost path (BLOCKING N2):** cost/span live in the OUTER `dispatch()` (`_attribute_cost_best_effort` at `:1579-1599`, span attrs `:1520-1569`), NOT inside `_dispatch_anthropic`. `prewarm()` replicates the span+cost tail with a synthetic step-context (§4.3) — do NOT call raw `_dispatch_anthropic` alone (that is shadow spend, violates AC item 5).
6. **Keep-alive self-disable (N5):** stop the loop after N consecutive failures (N=3), structured log, no auto-restart; do NOT trip the production `RetryBreakerRegistry` (§5).
7. **Model/provider gate (BLOCKING N6):** skip unless `"anthropic" in self.providers` (may be absent under `anthropic_optional`, `types.py:1526-1531`); no silent OpenAI fallback (§4.4 — the open model-source item).
8. **R2 (Q5):** explicit re-defer paragraph in the spec delta + clearance (§9). Phrase EXACTLY: "R2 auto-skip remains deferred until a committed cost-ceiling signal exists; the shipping defaults (opt-in-off + 1h-exclusion) already bound the C11 risk." Do NOT claim "opt-in-off fully discharges R2 forever."

Also noted (document, don't fix): **N7** daemon single-epoch reality — one daemon ctx ⇒ one `active_system_prompt` / `frozen_tool_superset` / `cache_ttl` for `SOFTWARE_ENGINEERING` (`cli/app.py:413`); keep-alive maintains only the parent-default SE epoch, not per-role/per-workflow (sibling of ADR-D4 §1.8, not a substitute). **N8** the `stage_5_loop_init.py:407-408` comment "bare becomes private constructor arg of the wrapper" is stale (bare is private to the HITL composer, which the retry wrapper then wraps) — don't copy it.

---

## 3. Scope reasoning (for the record)

- One-shot `harness run` IS a process boot (`cli/app.py:244-338` → `asyncio.run(_api_run(...))`); daemon is `harness daemon` (`cli/app.py:491` → `_daemon_main` at `:382`).
- Keep-alive only pays rent on the long-lived daemon (idle can exceed the 5min TTL between `run_workflow` invocations); a one-shot rarely idles 4min. So keep-alive = daemon-only.
- Pre-warm at stage 5 covers both process kinds from ONE seam (`run_bootstrap` is called by both `_api_run` and `_daemon_main`). Under opt-in-default-off, a one-shot operator who enables pre-warm accepts one `max_tokens=1` ping — intentional C11 posture, not a bug.

---

## 4. `prewarm()` on the BARE `RuntimeLLMDispatcher`

A focused method (NOT the full `dispatch()` pipeline — that runs skill-activation hooks + routing `infer` + inter-step injection that are inappropriate at boot). Returns a typed result enum: `WARMED` / `SKIPPED_NOT_ELIGIBLE` / `SKIPPED_NO_ANTHROPIC` / `FAILED` (for the keep-alive self-disable counter + test assertions).

### 4.1 Signature
`async def prewarm(self) -> PrewarmOutcome` on `RuntimeLLMDispatcher` (`llm_dispatch.py:447`). Uses only `self.*` constructor fields (all bound at stage 5): `self.providers`, `self.frozen_tool_superset`, `self.active_system_prompt`, `self.cache_ttl`, `self.workload_class`, `self.cost_chain`, `self.audit_writer`, `self.rate_table`, `self.cost_record_sink`, plus a tracer handle (see §4.3).

### 4.2 Eligibility gate (before any paid call)
Mirror the real breakpoint-placement gates so eligible ⟺ breakpoint-will-place:
```
if "anthropic" not in self.providers: return SKIPPED_NO_ANTHROPIC
if self.frozen_tool_superset is None:  return SKIPPED_NOT_ELIGIBLE
system = self.active_system_prompt
eligible = (
    _combined_prefix_clears_non_vacuity_floor(self.frozen_tool_superset, system)
    if system else
    _superset_clears_non_vacuity_floor(self.frozen_tool_superset)
)
if not eligible: return SKIPPED_NOT_ELIGIBLE   # log skipped_no_cacheable_prefix
```
Helpers exist: `_superset_clears_non_vacuity_floor` (`llm_dispatch.py:1806`), `_combined_prefix_clears_non_vacuity_floor` (`:1866`), `_ANTHROPIC_MIN_CACHEABLE_TOKENS=4096` (`:1800`).

### 4.3 The ping + honest cost/span
1. Build the minimal payload (ProviderAgnosticPayload is a frozen 3-tuple `messages`/`tools`/`params`, `cp_shared_types.py:89-107`):
   `ProviderAgnosticPayload(messages=({"role":"user","content":"cache prewarm"},), tools=None, params={"max_tokens": 1})`.
   (`max_tokens=0` from the ADR is invalid — `messages.create` requires ≥1, `llm_dispatch.py:1917`; adapt to 1, the 3c precedent.)
2. Open a span (tracer). Reuse the same span-open shape `dispatch()` uses (grep the `tracer.start_as_current_span(...)` / `_tracer` usage in `dispatch()` ~`:1120-1240` and the `gen_ai.operation` naming `:1610-1619`). A dedicated `llm.prewarm` operation token is acceptable — confirm against OD span-name discipline at build.
3. `resp, usage, cache_attrs, request_attrs = await _dispatch_anthropic(adapter, model, payload, system=self.active_system_prompt, upstream=None, frozen_tool_superset=self.frozen_tool_superset, cache_ttl=self.cache_ttl)` (`:2402`). This is where the `cache_control` breakpoint is placed (via `_payload_to_anthropic_kwargs`).
4. Set the `anthropic.cache_breakpoint_id` / `cache_ttl_seconds` / usage span attrs (reuse the `_set_if_present` block, `:1520-1569`).
5. `_attribute_cost_best_effort(span=span, cost_chain=self.cost_chain, audit_writer=self.audit_writer, rate_table=self.rate_table, cost_record_sink=self.cost_record_sink, provider_name="anthropic", model=model, parent_idempotency_key=<synthetic>, workflow_id="__prewarm__", parent_action_id=<synthetic>, input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, cache_creation=cache_attrs.cache_creation_input_tokens, cache_read=cache_attrs.cache_read_input_tokens, tenant_id=None)` (`:1579`). The synthetic `workflow_id="__prewarm__"` makes the spend visible/auditable (grok 3c: "process/audit/span, not last workflow's bill"); confirm the cost sink resolves to the bootstrap `_default` accumulator at boot-time (no active run) without crashing (`types.py:2081-2112` run-scoped proxy).
6. Return `WARMED`. Wrap 1-6 (from the paid call on) in try/except → on any provider exception, log + return `FAILED` (best-effort; never raise).

### 4.4 OPEN build-time item — the model string
`model` normally comes from `workflow.default_model_binding` (`api.py:257`), which is NOT available at bootstrap stage 5 / daemon boot (no workflow yet). Anthropic caches are per-model, so prewarm must warm the SAME model the real dispatches use. Resolution order to implement + verify at build:
1. If `ctx.routing_manifest` carries a default workload→binding that resolves to an anthropic model → use it. (Grep the routing_manifest shape; `stage_5_loop_init.py:361` binds it.)
2. Else if the operator declares a prewarm model (a new `prompt_cache_prewarm_model: str | None` config field) → use it.
3. Else → `SKIPPED_NOT_ELIGIBLE` (can't warm without a model; log it).
RuntimeConfig has NO bare default-model field (verified) — so option 2 (a small opt-in config field) is likely required. Decide at build; if adding the field, wire it into BOTH env loaders too (§6) OR keep it file/CLI-only (mirrors `prompt_cache_long_ttl_workloads`, which is collection/file-only per `cacheable_epoch.py:28-29`) — it does not gate correctness, only which model warms, so file/CLI-only is defensible.

---

## 5. Daemon keep-alive lifecycle (`_daemon_main`, `cli/app.py:382-489`)

- **Bare handle access:** `prewarm()` is on the bare dispatcher, but `ctx.llm_dispatcher` is the retry-wrapper. Expose the bare handle — preferred: stash the bare dispatcher on the mutable ctx at stage 5 (a new `ctx.bare_llm_dispatcher` field), mirroring how `routing_resolver=bare_dispatcher.resolve_routed_binding` is already handed to the wrapper (`stage_5_loop_init.py:507-508`). Alternative: a thin `prewarm()` passthrough on the wrapper (`return await self._bare.prewarm()` with an explicit `_bare` field). Pick the smaller diff at build.
- **Spawn:** after bootstrap bind (`cli/app.py:427`, after `_state["_harness_ctx"]=ctx`), if `config.prompt_cache_keepalive` AND `bare.cache_ttl == "5m"` (1h epochs excluded — ADR scope). Not spawned otherwise (byte-identical).
- **Loop body** (injectable sleep + interval for tests; default `asyncio.sleep`, 240s):
```
consec_fail = 0
while not ctx.drained_flag.is_set():
    await sleep(interval)
    if ctx.drained_flag.is_set(): break
    outcome = await bare.prewarm()
    if outcome is FAILED:
        consec_fail += 1
        if consec_fail >= 3: log("keepalive self-disabled after 3 failures"); break
    else:
        consec_fail = 0
```
  Prefer the `drained_flag` check over cancel-only so a long prewarm can still be interrupted.
- **Cancel+await placement (EXACT):** wrap the existing serve/drain race in a try; in a `finally` that runs BEFORE `await _shutdown(ctx)` (`:479-480`):
```
finally:
    if keepalive_task is not None:
        keepalive_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await keepalive_task        # MUST await, not only cancel
    await _shutdown(ctx)
    # socket unlink (existing)
```
  The keep-alive task is OUTSIDE the `{serve_task, drain_task}` race set, so the existing `pending` cancel loop does NOT cover it — the explicit finally is required (else "Task was destroyed but it is pending" or a prewarm mid-`_shutdown` against torn-down providers, `shutdown.py`).

---

## 6. Config fields (opt-in, default off)

On `RuntimeConfig` (defined in `config_source.py` + `types.py`):
- `prompt_cache_boot_prewarm: bool = False`
- `prompt_cache_keepalive: bool = False`
- (maybe) `prompt_cache_prewarm_model: str | None = None` — see §4.4.

The two bools gate cost-affecting behavior → wire into BOTH env loaders (`[[runtimeconfig-scalar-needs-both-env-loaders]]`), else silently dropped on the `HARNESS_*` path:
1. `config/loader.py` `_ENV_SCALAR_FIELDS` (`:68`) — `{field: (f"{PREFIX}NAME", _parse_bool)}` (precedent `effect_fencing`/`ollama_optional`/`routing_activation`).
2. `config_source.py` `_RuntimeEnvSettings` (`:149` area) — `field: bool | None = None`.
Add a `test_config_loader.py` + `test_config_source.py` env round-trip witness (`HARNESS_PROMPT_CACHE_KEEPALIVE=true` → `config.prompt_cache_keepalive is True`).

---

## 7. Test plan (hermetic — NO paid Anthropic calls; fake dispatcher + fake clock)

1. **Default-off control** — stage-5 + daemon with both flags False → zero prewarm calls (mock `bare.prewarm`, assert not called). Byte-identical.
2. **Opt-in boot ping (fail-on-main)** — flag on, fake anthropic adapter capturing kwargs → exactly one prewarm; assert `max_tokens==1` on the wire AND a `cache_control` breakpoint present on the composed tools/system block. Fails on main (no prewarm exists).
3. **Eligibility skip** — `frozen_tool_superset=None` → `SKIPPED_NOT_ELIGIBLE`, no adapter call; `"anthropic"` absent from providers → `SKIPPED_NO_ANTHROPIC`, no call; sub-4096-floor prefix → skip.
4. **Keep-alive fake clock** — inject fake sleep; assert prewarm fires each interval; assert ZERO pings when `cache_ttl=="1h"`.
5. **Self-disable** — fake prewarm returning FAILED → loop stops after exactly 3 calls, structured log; then no more.
6. **Drain cancels cleanly** — set `drained_flag` → keep-alive task cancelled+awaited, no "Task destroyed pending" warning, no leak.
7. **Cost record** — prewarm through the fake path appends a cost record to the sink with `workflow_id="__prewarm__"` (honest spend, AC item 5).
8. **Bootstrap-failure isolation** — a prewarm that raises at stage 5 does NOT fail `run_bootstrap` (assert bootstrap still returns a ctx; the exception is swallowed+logged).

---

## 8. Spec delta + posture

- **Runtime spec v1.97 → v1.98** — new subsection materializing ADR-D3 §1.5:189-190: pre-warm at stage 5 (both process kinds) + keep-alive daemon-only; opt-in-default-off; 5m-TTL-only keep-alive; eligibility gate; self-disable; best-effort-must-not-fail-bootstrap; N7 single-epoch reality documented; R2 re-defer paragraph (§9 exact wording).
- **Clearance marker** at `.harness/clearance/` (bundled-absorption arc). Decorrelated review = grok (`grok --prompt-file X --permission-mode auto --output-format plain`) + main-agent review.
- **Posture:** runtime-only. No CP/IS/OD/AS/ADR/CXA change. `ProviderAgnosticPayload` stays frozen (ADR-F1). Bundled-absorption (spec + impl + tests + clearance co-land).

---

## 9. R2 disposition — RE-DEFER (exact wording for the spec delta + clearance)

> R2 (the C11 "skip keep-alive under cost-ceiling pressure" carve-out, `u1-slice3b-epoch-partition-design.md` §3.3) auto-skip remains DEFERRED until a committed cost-ceiling signal exists in-substrate. Persona §6 records the cost ceiling as operator-asserted with no cell matrix, so an automatic skip-under-pressure has no committed signal to key on — building one would be X-AL-3 design extension. The shipping defaults (opt-in-default-off + the 5m-TTL-only / 1h-excluded keep-alive) already bound the C11 risk. Register item (6) explicitly permits "build the carve-out OR explicitly re-defer with rationale."

---

## 10. Build order (remaining — no code written yet)

1. Config fields + BOTH env loaders (§6) + env round-trip tests.
2. `PrewarmOutcome` enum + `prewarm()` on the bare `RuntimeLLMDispatcher` (§4) + eligibility/ping/cost tests (7.2, 7.3, 7.7).
3. Model-source resolution (§4.4) — ground the routing_manifest shape; decide config field.
4. Stage-5 best-effort prewarm wiring (§1) + bare-handle stash on ctx (§5) + bootstrap-isolation test (7.8).
5. Daemon keep-alive task + cancel/finally + self-disable (§5) + tests (7.4, 7.5, 7.6).
6. Default-off control test (7.1).
7. Runtime spec v1.98 delta + clearance marker (§8, §9).
8. `just check` → 0/0/0 pyright + green suites; fix caches if reds (`[[just-check-provider-secret-env-artifact]]`).
9. grok post-build diff review to convergence (out-of-family); fold blocking.
10. `ship-pr` → PR → operator merge AUQ → §12.2.1 fixed-point refresh.

---

## 11. Reviewer note (durable)

Super Grok CLI (`grok` 0.2.93 at `~/.local/bin/grok`, model grok-4.5, grok.com login) is the operator-designated replacement for the down out-of-family Codex reviewer. Headless invocation: `grok --prompt-file <path> --permission-mode auto --output-format plain` — runs single-turn, reads repo files to self-ground (verified), prints to stdout, $0 on the SuperGrok subscription (X-AL-1 H_E dev tooling, NOT H_T's provider). Both reviewer roles per arc: pre-build design-packet review (this DDR) + post-build diff review. Pairs with the Fable-5 `Agent(model:"fable")` fallback if grok is also unavailable. → save to memory at the arc gate (fold into `[[codex-out-of-family-reviewer]]`).
