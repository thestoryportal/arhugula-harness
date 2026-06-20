# Class 1 Fork — B-INTERSTEP-PERRUN-ISOLATION (per-run ContextVar isolation of run-scoped holders)

**Filed:** 2026-06-20 · R-FS-1 standalone `B-*` arc **B-INTERSTEP-PERRUN-ISOLATION** (the registered B-INTERSTEP follow-on §3/§5; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md`). Bundled-absorption posture: runtime spec **v1.63 → v1.64** (§14.21.5 invariant 7 AMENDED → CLOSED + §14.21.7 follow-on marked BUILT — NO new contract) + `harness-runtime/src` + by-execution tests. Class 1 (X-AL-3 design-substrate amendment of a cleared spec). Design back-flow **FULL-SPEC-pre-authorized** (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + design decided — the mechanism was already prescribed by the **B-INTERSTEP fork §3/§5** (this arc implements it). **NO operator gate.** The change is additive correctness that SACRIFICES no committed invariant — it *removes* B-INTERSTEP's per-loop single-flight serialization and *closes* a registered residual (the timeout-zombie). The opt-out default (channel unbound) is byte-identical; the always-on cost path's single-run output is unchanged (daemon multi-run goes buggy→correct, no regression). No nameable cross-domain tension (internal concurrency correctness — not a C10⊥C11 or any voice-pair fork) → advisor + out-of-family Codex, **not council** (the same §10.9 discriminator the B-INTERSTEP fork applied). Adopt-and-note per workspace `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`.

---

## §1 The fork — the run-scoped holders are bootstrap-scoped, so daemon-reuse leaks across runs

B-INTERSTEP's `InterStepOutputChannel` (and the sibling always-on `CostRecordAccumulator`, §82 Class-3) are allocated at **bootstrap** scope on the frozen `HarnessContext`. In daemon-client mode (U-RT-108) ONE bootstrapped ctx serves many `run_workflow` invocations (the spec line-631 concurrency invariant: distinct MCP clients run concurrent INDEPENDENT runs), so concurrent runs SHARE the one holder. B-INTERSTEP's §14.21.5 **invariant 7** (run-scoped-no-cross-run-leak) was honestly **bounded** to three cases:

- **(a) sequential reuse** — closed by a per-run `reset()` at the `run_workflow` boundary.
- **(b) concurrent-within-drain-timeout** — closed by a per-running-loop single-flight **lock** wrapping `[reset + execute]` when the channel is bound (the opt-out default never locks).
- **(c) the concurrent-WITH-timeout `to_thread`-zombie** — **NOT closed**: a run exceeding `drain_timeout_seconds` raises `TimeoutError` (the `async with` releases the lock) but the non-cancellable `asyncio.to_thread` worker keeps running and recording into the SHARED holder, so a following run can reset/interleave with it. A released lock cannot fence a zombie.

The B-INTERSTEP fork §5 round-5 named (c) the **SYSTEMIC reused-ctx daemon timeout-zombie exposure shared by EVERY mutable holder on the bootstrap ctx** (`cost_record_accumulator`, ledger writers, …) and registered the proper fix — "a channel-only run-key would be a **false-complete** (one holder safe, siblings still corrupt under the same trigger)."

### §1.1 The mechanism was prescribed (no novel design)

The B-INTERSTEP fork §3 prescribed the fix verbatim: **"a `ContextVar`-bound channel resolved at dispatch"** that closes THREE things — removes the (7b) serialization + closes the (7c) timeout-zombie (a per-run channel means a timed-out run's zombie writes only its OWN dead channel) + closes the IDENTICAL `cost_record_accumulator` exposure (§82 Class-3). This arc implements that prescription. No re-decision is required; the design authority is the cleared B-INTERSTEP fork.

---

## §2 Resolution — ContextVar-bound per-run holders behind stable ctx proxies

### §2.1 Mechanism (the fork-prescribed shape; empirically grounded)

1. A module-level `ContextVar` per run-scoped holder (`INTER_STEP_CHANNEL_VAR` in `lifecycle/inter_step_output_channel.py`; `COST_ACCUM_VAR` in `types.py`), default `None`.
2. The frozen `HarnessContext` binds a stable **proxy** (`RunScopedInterStepOutputChannel` / `RunScopedCostRecordAccumulator`, each a subclass of the holder type so it IS-A the field type) that delegates every method/attr to `var.get()` — the current run's holder, or a bound bootstrap default when no run is active (direct-stage / child paths). Consumers (LLM dispatcher, CP driver, `_build_run_result`, cost wrappers) read through the proxy **unchanged**.
3. The `run_workflow` handler sets a fresh holder per run: the channel (opt-in, fresh per invocation) + the cost accumulator (fresh iff still `None` — see §2.2). The set propagates into the `asyncio.to_thread(execute_workflow)` worker via `contextvars.copy_context()`. The B-INTERSTEP single-flight lock + `reset()` are **removed**.
4. The per-dispatch cost wrappers now thread the accumulator **PROXY** (`ctx.cost_record_accumulator`) as their `cost_record_sink`, NOT `ctx.cost_record_accumulator.records` — the captured-list that defeated isolation. The sink param type is widened to a `SupportsCostRecordAppend` Protocol (satisfied by `list` AND the proxy) in a leaf module to avoid an import cycle (`types` imports `webhook_delivery_composer`).

### §2.2 The empirically-grounded asymmetry — caller-set vs handler-set

A probe of the in-process MCP path (`create_connected_server_and_client_session` → tool handler → `asyncio.to_thread`) established: a ContextVar set in the **caller** propagates DOWN to the handler + worker AND is retained by the caller after the call; a value set in the **handler** does NOT propagate back UP to the caller. So:

- **`api.run`/`resume` (single-run, serialized by `_run_lock`, fresh bootstrap per call):** set a fresh `COST_ACCUM_VAR` around `[invoke + cost-read]`. The handler inherits it (skips its fresh-if-`None` set), the worker's wrappers append to it, and the post-run `ctx.cost_record_accumulator.records` read resolves the SAME accumulator. The `finally` reset prevents leakage into a later direct-stage test on a reused task.
- **daemon path (no `api.run` caller):** the `run_workflow` handler sees `COST_ACCUM_VAR is None` → establishes the per-run accumulator itself, so concurrent daemon runs do not share one. The channel (read only inside the run) is always set fresh by the handler when opt-in.

### §2.3 Non-vacuity is the deliverable (advisor)

The arc's reason to exist is closing (7c) + removing the (7b) lock — so the load-bearing proof is a test that **reproduces cross-run corruption under the timeout-zombie trigger WITHOUT isolation and shows it closed WITH it, the lock deleted, for both holders**: `test_timeout_zombie_writes_only_its_own_per_run_channel` (REAL `asyncio.to_thread` copy_context — A's timed-out zombie writes channel A, not B) + the negative control `test_negative_control_shared_channel_timeout_zombie_corrupts`; plus concurrent-isolation + cost-isolation, each with a negative control; plus the freeze-by-reference + per-run-resolution end-to-end re-proof at `test_bootstrap.py`.

---

## §3 Scope — both named holders; other holders assessed (not a false-complete)

| Holder | Disposition |
|---|---|
| `inter_step_output_channel` | **ISOLATED** (opt-in proxy + `INTER_STEP_CHANNEL_VAR`). |
| `cost_record_accumulator` | **ISOLATED** (always-on proxy + `COST_ACCUM_VAR`; §82 Class-3 — the IDENTICAL exposure). |
| `resume_context_holder` | NOT isolated — set-per-run overwrite (one-shot), not accumulating shared contents. |
| `engine_output_store` | NOT isolated — durable store keyed by `run_idempotency_key` (per-run keyed already). |
| ledger writers | NOT isolated — ADR-F2 single-writer + run_id-tagged entries (a reader filters by run_id); no shared mutable accumulation corruptible across runs. |

The generic proxy primitive composes for any future bootstrap-ctx holder that DOES accumulate run-scoped contents — so the "channel-only false-complete" the fork warned of is avoided, and the symmetric "silently bound-to-two" false-complete is avoided by documenting each other holder's disposition rather than silently ignoring it.

---

## §4 Why this is X-AL-3-clean (not silent absorption)

| X-AL-3 obligation | Discharge |
|---|---|
| New/changed design surface routed to design back-flow before impl | This fork doc (Class 1) + runtime spec v1.63 → v1.64 §14.21.5/§14.21.7 amendment + clearance marker, all in the bundled-absorption PR |
| Back-flow doc co-lands with the design-substrate edit (CI guard) | This fork doc + `Spec_Harness_Runtime-v1_64-cleared-2026-06-20.md` |
| No committed-invariant sacrifice without an operator gate | None sacrificed — additive correctness; the opt-out default + the dispatch signature + §25.3.3.4 PRESERVED; the lock removal + invariant-7 closure tighten, not relax |
| Registered (not silent-deferred) residual | Other holders' dispositions documented (§3); no new residual introduced |

---

## §5 Decorrelated review

- **advisor (full-transcript, pre-build):** affirmed the ContextVar + stable-proxy shape (Option A) as composing with the existing `_CURRENT_TOOL_CTX` per-task pattern; flagged the load-bearing deliverable (the timeout-zombie negative-control test), an opt-out byte-identical bug-in-waiting (bind the channel proxy ONLY when opt-in — caught + applied), the always-on cost path as the real risk (enumerate its full surface — done; re-run arc-CA cost tests — green), and the `child_workflow_runner` ContextVar-inheritance blind-spot (verified inherits). No council (no nameable cross-domain tension).
- **out-of-family Codex (pre-merge, on the diff):** the identical concurrency hazard class as B-INTERSTEP (which Codex caught 5 real bugs in) — to be run before merge.

## §6 Gates (impl)

pyright 0/0/0 (changed files) · ruff · the timeout-zombie deliverable + concurrent-isolation + cost-isolation tests (each with a negative control) + the freeze-by-reference re-proof green · harness-runtime 1972 passed / 13 skipped · harness-cp 1093 passed / 1 xfailed · no §5.2-hash change. Bundled-absorption: runtime spec v1.64 + this fork doc + clearance marker + `harness-runtime` impl + by-execution tests + spine-ledger BUILT + roadmap.html.
